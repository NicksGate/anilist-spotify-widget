# Spotify listening card for an AniList bio

This project creates a dark Spotify-style SVG card showing the current track and three recent tracks. GitHub Actions refreshes it about every five minutes.

## Important requirements

- Your Spotify account needs **Spotify Premium** for a Spotify Developer app in Development Mode under Spotify's current rules.
- Your Spotify account must be added as a user of your app if Spotify asks for an allowlist.
- AniList must allow externally hosted images in the bio for the image to display. If SVG images are blocked, use the Pages URL as a normal link instead.

## 1. Create a Spotify app

1. Open https://developer.spotify.com/dashboard
2. Create an app.
3. Open its settings and add this exact Redirect URI: `http://127.0.0.1:8888/callback`
4. Save. Copy the Client ID and Client Secret somewhere private.

## 2. Get your refresh token

Install Python 3 if it is not already installed: https://www.python.org/downloads/

Download or clone this repository to your computer. Open a terminal in the project folder and run:

```bash
python auth.py
```

On some Windows systems, use `py auth.py`.

Paste your Spotify Client ID and Client Secret when prompted, then approve the Spotify permission request in your browser. The terminal will print three values. Keep them private.

## 3. Create a GitHub repository

1. Create a new repository at https://github.com/new. A public repository is needed for a public GitHub Pages site.
2. Upload all files from this project, including the hidden `.github/workflows/update-widget.yml` file.
3. In the repository, go to **Settings → Secrets and variables → Actions → New repository secret**.
4. Add these secrets with the exact names:
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`
   - `SPOTIFY_REFRESH_TOKEN`

Never put credentials in `update_widget.py`, `auth.py` commits, or your AniList bio.

## 4. Turn on GitHub Pages

1. Open **Settings → Pages**.
2. Under the build/deployment source, choose **Deploy from a branch**.
3. Choose branch `main` and folder `/(root)`, then save.
4. Wait for GitHub to publish the site. Its address will look like `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/`.

## 5. Run the workflow

1. Open the repository's **Actions** tab.
2. Select **Update Spotify widget**.
3. Click **Run workflow** and confirm.
4. Wait for the run to finish. It should update `spotify.svg` in the repository.
5. Open `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/spotify.svg` to view your card.

The schedule attempts to refresh every five minutes; GitHub can delay scheduled runs. If the first run fails, open its log in Actions and check that all three secrets are spelled correctly.

## 6. Add it to AniList

Try this Markdown in your AniList bio, replacing the URL with your actual Pages address:

```markdown
![My Spotify listening status](https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/spotify.svg)
```

If AniList does not render it, try a plain link:

```markdown
[🎵 My Spotify listening status](https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/spotify.svg)
```

## Privacy and maintenance

The SVG is public, so anyone who can see your AniList bio may see the song and artist names displayed on it. The Client Secret and refresh token must remain GitHub Actions secrets. Spotify refresh tokens can expire or be revoked; if the workflow starts failing with an authorization error, run `auth.py` again and update the `SPOTIFY_REFRESH_TOKEN` repository secret.
