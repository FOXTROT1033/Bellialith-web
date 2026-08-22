import os
import secrets
import sqlite3
from datetime import timedelta
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request, session, send_from_directory

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WEB_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(WEB_DIR, "web.db")

load_dotenv(os.path.join(WEB_DIR, ".env"))

app = Flask(
    __name__,
    static_folder=None,
)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is not configured in web/.env")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "true").lower() == "true",
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
)

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")

if not DISCORD_CLIENT_ID or not DISCORD_CLIENT_SECRET or not DISCORD_REDIRECT_URI:
    raise RuntimeError(
        "DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET and "
        "DISCORD_REDIRECT_URI must be configured in web/.env"
    )

DISCORD_API = "https://discord.com/api/v10"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_db()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            discord_id TEXT PRIMARY KEY,
            username TEXT,
            avatar_hash TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


def avatar_url(user):
    avatar_hash = user.get("avatar")

    if not avatar_hash:
        discriminator = user.get("discriminator", "0")

        try:
            index = int(discriminator) % 5
        except (TypeError, ValueError):
            index = 0

        return f"https://cdn.discordapp.com/embed/avatars/{index}.png"

    return (
        f"https://cdn.discordapp.com/avatars/"
        f"{user['id']}/{avatar_hash}.png?size=256"
    )


def require_configured_oauth():
    return all(
        [
            DISCORD_CLIENT_ID,
            DISCORD_CLIENT_SECRET,
            DISCORD_REDIRECT_URI,
        ]
    )


@app.route("/auth/discord")
def discord_login():
    if not require_configured_oauth():
        return "Discord OAuth2 is not configured.", 503

    state = secrets.token_urlsafe(32)

    session["oauth_state"] = state
    session.permanent = True

    params = {
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify",
        "state": state,
        "prompt": "consent",
    }

    return redirect(
        "https://discord.com/oauth2/authorize?"
        + urlencode(params)
    )


@app.route("/auth/discord/callback")
def discord_callback():
    if request.args.get("error"):
        session.pop("oauth_state", None)
        return redirect("/login.html?error=discord_denied")

    code = request.args.get("code")
    state = request.args.get("state")

    if not code or not state:
        return redirect("/login.html?error=oauth_failed")

    stored_state = session.pop("oauth_state", None)

    if not stored_state or not secrets.compare_digest(
        stored_state,
        state,
    ):
        return redirect("/login.html?error=invalid_state")

    try:
        token_response = requests.post(
            f"{DISCORD_API}/oauth2/token",
            data={
                "client_id": DISCORD_CLIENT_ID,
                "client_secret": DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": DISCORD_REDIRECT_URI,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=10,
        )

        if token_response.status_code != 200:
            app.logger.error(
                "Discord token exchange failed: %s",
                token_response.status_code,
            )
            return redirect("/login.html?error=oauth_failed")

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return redirect("/login.html?error=oauth_failed")

        user_response = requests.get(
            f"{DISCORD_API}/users/@me",
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            timeout=10,
        )

        if user_response.status_code != 200:
            app.logger.error(
                "Discord user request failed: %s",
                user_response.status_code,
            )
            return redirect("/login.html?error=oauth_failed")

        user = user_response.json()

    except requests.RequestException:
        app.logger.exception("Discord OAuth request failed")
        return redirect("/login.html?error=oauth_failed")

    discord_id = user["id"]
    username = (
        user.get("global_name")
        or user.get("username")
        or "Discord User"
    )
    avatar_hash = user.get("avatar")

    connection = get_db()

    connection.execute(
        """
        INSERT INTO users (
            discord_id,
            username,
            avatar_hash
        )
        VALUES (?, ?, ?)

        ON CONFLICT(discord_id)
        DO UPDATE SET
            username = excluded.username,
            avatar_hash = excluded.avatar_hash,
            last_login = CURRENT_TIMESTAMP
        """,
        (
            discord_id,
            username,
            avatar_hash,
        ),
    )

    connection.commit()
    connection.close()

    # The Discord access token is intentionally NOT stored.
    session.clear()
    session.permanent = True

    session["discord_id"] = discord_id
    session["username"] = username
    session["avatar_url"] = avatar_url(user)

    return redirect("/")


@app.route("/auth/logout")
def logout():
    session.clear()
    return redirect("/login.html?logged_out=1")


@app.route("/api/me")
def current_user():
    discord_id = session.get("discord_id")

    if not discord_id:
        return jsonify({"authenticated": False}), 401

    return jsonify(
        {
            "authenticated": True,
            "discord_id": discord_id,
            "username": session.get("username"),
            "avatar_url": session.get("avatar_url"),
        }
    )


def is_authenticated():
    return bool(session.get("discord_id"))


@app.route("/")
def home():
    # Bellialith requires Discord authentication before entering the main site.
    if not is_authenticated():
        return redirect("/login")
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/login")
def login():
    # A logged-in user should not be sent back to the login screen.
    if is_authenticated():
        return redirect("/dashboard")
    return send_from_directory(BASE_DIR, "login.html")


# Explicit public page routes. These avoid relying on the catch-all route
# for normal site navigation and make every HTML page directly addressable.
_PAGE_FILES = {
    "index": "index.html",
    "login": "login.html",
    "features": "features.html",
    "commands": "commands.html",
    "updates": "updates.html",
    "privacy": "privacy.html",
    "terms": "terms.html",
    "dashboard": "dashboard.html",
    "profile": "profile.html",
}


_PROTECTED_PAGES = set(_PAGE_FILES) - {"login"}


def serve_page(page_name):
    if page_name in _PROTECTED_PAGES and not is_authenticated():
        return redirect("/login")
    if page_name == "login" and is_authenticated():
        return redirect("/dashboard")
    return send_from_directory(BASE_DIR, _PAGE_FILES[page_name])


for _page_name, _filename in _PAGE_FILES.items():
    # Keep the legacy .html URLs working.
    app.add_url_rule(
        f"/{_filename}",
        endpoint=f"page_{_page_name}_html",
        view_func=lambda page_name=_page_name: serve_page(page_name),
    )

    # Public clean URLs used by the website navigation.
    app.add_url_rule(
        f"/{_page_name}",
        endpoint=f"page_{_page_name}",
        view_func=lambda page_name=_page_name: serve_page(page_name),
    )




@app.route("/<path:path>")
def site_files(path):
    # Never expose backend files, environment variables or the SQLite DB.
    blocked = (
        path.startswith("web/"),
        path == ".env",
        path.startswith(".git/"),
        path.endswith(".db"),
    )

    if any(blocked):
        return "Not Found", 404

    requested = os.path.join(BASE_DIR, path)

    if os.path.isfile(requested):
        return send_from_directory(BASE_DIR, path)

    # Do not silently expose the Home page for unknown routes.
    if not is_authenticated():
        return redirect("/login")

    return send_from_directory(BASE_DIR, "index.html")


if __name__ == "__main__":
    init_database()

    # Pterodactyl provides SERVER_PORT automatically.
    # The application must listen on 0.0.0.0 so the panel can reach it.
    port = int(os.getenv("SERVER_PORT", "25579"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )