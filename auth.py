"""One-time local helper to get a Spotify refresh token."""
import base64
import json
import os
import secrets
import threading
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = "user-read-currently-playing user-read-recently-played"
auth_code = None
auth_error = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code, auth_error
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return
        if "error" in params:
            auth_error = params["error"][0]
            body = b"Spotify authorization was cancelled. You can close this tab."
        elif "code" in params:
            auth_code = params["code"][0]
            body = b"Spotify connected! You can close this tab and return to the terminal."
        else:
            body = b"No authorization code was received."
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass

def main():
    client_id = input("Paste your Spotify Client ID: ").strip()
    client_secret = input("Paste your Spotify Client Secret: ").strip()
    if not client_id or not client_secret:
        raise SystemExit("Client ID and Client Secret are both required.")

    state = secrets.token_urlsafe(16)
    server = HTTPServer(("127.0.0.1", 8888), CallbackHandler)
    server.timeout = 180
    query = urllib.parse.urlencode({
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": state,
    })
    url = "https://accounts.spotify.com/authorize?" + query
    print("\nOpening Spotify authorization in your browser.")
    print("If it does not open, copy this URL into your browser:\n", url, "\n")
    import webbrowser
    webbrowser.open(url)
    server.handle_request()
    server.server_close()

    if auth_error:
        raise SystemExit("Spotify authorization failed: " + auth_error)
    if not auth_code:
        raise SystemExit("Timed out waiting for Spotify. Run this script again.")
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
    }).encode()
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=data,
        headers={
            "Authorization": "Basic " + credentials,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.load(response)
    refresh_token = result.get("refresh_token")
    if not refresh_token:
        raise SystemExit("Spotify did not return a refresh token. Try authorizing again.")
    print("\nSUCCESS. Add these three values as GitHub repository Actions secrets:")
    print("SPOTIFY_CLIENT_ID =", client_id)
    print("SPOTIFY_CLIENT_SECRET =", client_secret)
    print("SPOTIFY_REFRESH_TOKEN =", refresh_token)
    print("\nTreat the Client Secret and Refresh Token like passwords. Do not post them publicly.")

if __name__ == "__main__":
    main()
