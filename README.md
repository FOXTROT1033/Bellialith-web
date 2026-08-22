# Bellialith Website

Official website for Bellialith, a Discord character-collecting bot.

Bellialith is built around character collection, rolls, progression,
economy, inventory, rewards and other Discord gameplay systems.

## Website

The website is a static HTML/CSS project designed around Bellialith's
visual identity.

### Pages

- `index.html` — main landing page
- `features.html` — Bellialith features and gameplay systems
- `commands.html` — command documentation
- `updates.html` — website and Bellialith updates
- `privacy.html` — Privacy Policy
- `terms.html` — Terms of Service
- `style.css` — shared website styling
- `assets/` — artwork, logos and other website assets

## Features

The website currently presents:

- Character collection
- Rolls
- Collections
- Economy
- Coins and XP
- Shop
- Inventory
- Reward Boxes
- Discord bot commands
- Bellialith updates
- Privacy and Terms pages

## Commands

Bellialith uses Discord slash commands.

Current documented commands include:

### General

- `/help`
- `/hello`
- `/profile`
- `/botprofile`
- `/balance`

### Characters

- `/roll`
- `/claim`
- `/collection`
- `/characters`
- `/sell`

### Economy

- `/daily`
- `/shop`
- `/buy`

### Inventory

- `/inventory`
- `/use`

The command list may change as Bellialith continues to develop.

## Design

The website follows the Bellialith visual identity using:

- Dark monochrome visuals
- Bellialith artwork
- Cinzel typography
- Inter typography
- Transparent panels
- Minimal borders
- Character-focused layouts

## GitHub Pages

This is a static website and can be deployed using GitHub Pages.

## Development

The website is maintained separately from the Bellialith Discord bot.

Changes should be tested locally before being committed and pushed
to the repository.

## Project Status

Bellialith and its website are actively being developed.

Features, commands, documentation and visual elements may change
as development continues.


## Discord Login / Web Backend

The website now includes a Flask backend for Discord OAuth2.

### Local setup

From `StoatBot/web`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy `web/.env.example` to `web/.env` and fill in:

- `DISCORD_CLIENT_ID`
- `DISCORD_CLIENT_SECRET`
- `DISCORD_REDIRECT_URI`
- `FLASK_SECRET_KEY`

For local testing, use a localhost redirect URI in the Discord Developer
Portal and set the same value in `.env`, for example:

`http://127.0.0.1:5000/auth/discord/callback`

Also set `COOKIE_SECURE=false` locally because local HTTP does not use HTTPS.

Then start the backend:

```powershell
python app.py
```

Open the website through Flask:

`http://127.0.0.1:5000/login.html`

Do not open `login.html` directly with `file://`. The `/auth/discord`
route belongs to the Flask backend.

### Security notes

The website never receives a Discord password.

The OAuth2 authorization code is exchanged server-side. The Discord
access token is used only for the account lookup and is deliberately not
stored in the Bellialith database.

The session contains the Discord user ID and basic display information.
The database currently stores the Discord ID, display name, avatar hash,
creation time and last login time.

The next phase will connect the authenticated Discord ID to Bellialith's
existing bot/profile data and add the profile editor.
