# Bellialith Website

Official website for **Bellialith**, a Discord character-collecting bot.

Bellialith is built around character collection, rolls, progression, economy, inventory, rewards and other Discord gameplay systems.

The website provides the public Bellialith experience, documentation, updates, legal information and authenticated user features.

## Website

The Bellialith website combines a visual HTML/CSS frontend with a Flask backend used for Discord authentication and authenticated pages.

### Pages

* `index.html` — main landing page
* `features.html` — Bellialith features and gameplay systems
* `commands.html` — command documentation
* `updates.html` — Bellialith and website updates
* `dashboard.html` — authenticated user dashboard
* `profile.html` — authenticated user profile
* `login.html` — Discord login page
* `privacy.html` — Privacy Policy
* `terms.html` — Terms of Service
* `style.css` — shared website styling
* `assets/` — artwork, logos and other website assets
* `web/` — Flask backend and authentication system
* `tests/` — website/backend tests

## Features

The website currently presents:

* Character collection
* Character rolls
* Collections
* Economy
* Coins and XP
* Shop
* Inventory
* Reward Boxes
* Discord bot commands
* Bellialith updates
* Discord OAuth2 login
* Secure session-based authentication
* Authenticated dashboard
* User profile
* Privacy Policy
* Terms of Service

## Commands

Bellialith uses Discord slash commands.

Current documented commands include:

### General

* `/help`
* `/hello`
* `/profile`
* `/botprofile`
* `/balance`

### Characters

* `/roll`
* `/claim`
* `/collection`
* `/characters`
* `/sell`

### Economy

* `/daily`
* `/shop`
* `/buy`

### Inventory

* `/inventory`
* `/use`

The command list may change as Bellialith continues to develop.

## Discord Login

The website supports Discord OAuth2 authentication through the Flask backend.

Users can sign in with their Discord account without entering their Discord password into Bellialith.

After authentication, the website can identify the Discord account and provide access to authenticated Bellialith pages.

The authentication flow is handled through Discord's official OAuth2 authorization system.

## Web Backend

The website uses Flask for backend functionality.

The backend currently handles:

* Discord OAuth2 authentication
* Login
* Logout
* Session management
* Discord account lookup
* Authenticated page access
* Basic user profile information

The Discord access token is used for the account lookup and is deliberately not stored in the Bellialith database.

The session contains the Discord user ID and basic display information.

The database currently stores:

* Discord ID
* Display name
* Avatar hash
* Account creation time
* Last login time

The authenticated Discord ID will eventually be connected to Bellialith's existing bot/profile data.

## Local Development

### Requirements

* Python 3
* A Discord application configured through the Discord Developer Portal
* Git

### Backend setup

From the website's `web` directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy:

```text
web/.env.example
```

to:

```text
web/.env
```

Then configure:

```text
DISCORD_CLIENT_ID=
DISCORD_CLIENT_SECRET=
DISCORD_REDIRECT_URI=
FLASK_SECRET_KEY=
```

For local development, use a localhost redirect URI configured in the Discord Developer Portal.

Example:

```text
http://127.0.0.1:5000/auth/discord/callback
```

Set:

```text
COOKIE_SECURE=false
```

when testing locally over HTTP.

### Start the backend

From `web/`:

```powershell
python app.py
```

Then open:

```text
http://127.0.0.1:5000/login.html
```

Do not open `login.html` directly using `file://`.

The Discord authentication routes are provided by the Flask backend.

## Security

Bellialith does not request, receive or store Discord passwords.

The OAuth2 authorization code is exchanged server-side.

Discord access tokens are not stored in the Bellialith database.

Authentication sessions are handled by the Flask backend and protected using server-side session configuration.

Production authentication should always use HTTPS and secure cookies.

Sensitive configuration such as Discord client secrets and Flask secret keys must remain in `.env` and must never be committed to the repository.

## Design

The website follows the Bellialith visual identity using:

* Dark monochrome visuals
* Bellialith artwork
* Cinzel typography
* Inter typography
* Transparent panels
* Minimal borders
* Gothic-inspired visual elements
* Character-focused layouts
* High-contrast white typography
* Black and grayscale backgrounds

The website is designed to maintain the same visual identity across public and authenticated pages.

## Project Structure

```text
Bellialith-web/
│
├── assets/
│   └── Website artwork, logos and visual assets
│
├── tests/
│   └── Website and backend tests
│
├── web/
│   ├── app.py
│   ├── requirements.txt
│   ├── .env.example
│   └── ...
│
├── commands.html
├── dashboard.html
├── features.html
├── index.html
├── login.html
├── privacy.html
├── profile.html
├── terms.html
├── updates.html
├── style.css
└── README.md
```

## Development Guidelines

Changes should be tested locally before being committed and pushed to the repository.

When modifying authenticated functionality, test at minimum:

* Login
* Discord OAuth2 callback
* Authenticated page access
* Logout
* Session behavior
* Public page access
* Mobile/responsive layouts

Do not commit:

* `.env` files
* Discord client secrets
* Flask secret keys
* Local databases containing sensitive data
* Python virtual environments
* Temporary development files

## Deployment

The website requires a Flask-capable server for its authentication features.

Because Discord OAuth2 and authenticated sessions require a backend, the complete website cannot be deployed as a purely static GitHub Pages site.

The production deployment must provide:

* HTTPS
* Flask/Python runtime
* Persistent database storage
* Environment variables
* Discord OAuth2 configuration
* Correct production redirect URI
* Secure cookies

## Project Status

Bellialith and its website are actively being developed.

The current website includes the public Bellialith experience, documentation, legal pages and Discord authentication.

The next development phase will connect authenticated Discord accounts to Bellialith's existing bot/profile data and expand the profile and dashboard systems.

Features, commands, documentation and visual elements may change as development continues.
