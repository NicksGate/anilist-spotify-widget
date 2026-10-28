"""Fetch Spotify listening data and render a dark Spotify-style SVG card."""
import base64
import html
import json
import os
import urllib.parse
import urllib.request
import urllib.error

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]

def request_json(url, headers=None, data=None):
    req = urllib.request.Request(url, headers=headers or {}, data=data)
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            if response.status == 204:
                return None
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 204:
            return None
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Spotify API returned HTTP {exc.code}: {body[:400]}") from exc

def get_access_token():
    credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
    }).encode()
    result = request_json(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": "Basic " + credentials,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data=data,
    )
    return result["access_token"]

def api_get(path, token):
    return request_json(
        "https://api.spotify.com/v1/" + path,
        headers={"Authorization": "Bearer " + token},
    )

def safe(value):
    return html.escape(str(value or ""), quote=True)

def get_art(item):
    images = (item.get("album") or {}).get("images") or []
    return images[0].get("url", "") if images else ""

def artists(item):
    return ", ".join(a.get("name", "") for a in item.get("artists", [])) or "Unknown artist"

def render_svg(current, recent):
    width, height = 800, 510
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="800" height="510" rx="24" fill="#121212"/>',
        '<rect x="1" y="1" width="798" height="508" rx="23" fill="none" stroke="#303030"/>',
        '<circle cx="45" cy="43" r="18" fill="#1DB954"/>',
        '<path d="M35 39 Q45 34 55 40 M37 45 Q45 41 53 46 M39 50 Q45 47 51 51" fill="none" stroke="#101010" stroke-width="2.5" stroke-linecap="round"/>',
        '<text x="75" y="40" fill="#FFFFFF" font-family="Arial, sans-serif" font-size="23" font-weight="700">MY SPOTIFY</text>',
        '<text x="75" y="59" fill="#B3B3B3" font-family="Arial, sans-serif" font-size="11" letter-spacing="2">LISTENING STATUS</text>',
        '<rect x="650" y="27" width="115" height="28" rx="14" fill="#1D3B2A"/>',
        '<circle cx="666" cy="41" r="4" fill="#1DB954"/>',
        '<text x="678" y="45" fill="#1DB954" font-family="Arial, sans-serif" font-size="11" font-weight="700">AUTO UPDATE</text>',
        '<text x="28" y="102" fill="#1DB954" font-family="Arial, sans-serif" font-size="13" font-weight="700" letter-spacing="1.5">NOW PLAYING</text>',
    ]
    if current and current.get("item") and current.get("currently_playing_type") == "track":
        item = current["item"]
        title = item.get("name", "Unknown track")
        artist = artists(item)
        link = (item.get("external_urls") or {}).get("spotify", "https://open.spotify.com/")
        art = get_art(item)
        if art:
            out.append(f'<image href="{safe(art)}" x="28" y="120" width="138" height="138" preserveAspectRatio="xMidYMid slice"/>')
        else:
            out.append('<rect x="28" y="120" width="138" height="138" rx="8" fill="#282828"/>')
        out += [
            f'<a href="{safe(link)}"><text x="188" y="161" fill="#FFFFFF" font-family="Arial, sans-serif" font-size="25" font-weight="700">{safe(title[:42])}</text></a>',
            f'<text x="188" y="190" fill="#B3B3B3" font-family="Arial, sans-serif" font-size="17">{safe(artist[:55])}</text>',
            f'<text x="188" y="222" fill="#1DB954" font-family="Arial, sans-serif" font-size="13">{"▶ PLAYING NOW" if current.get("is_playing") else "Ⅱ PAUSED"}</text>',
            f'<text x="188" y="246" fill="#777777" font-family="Arial, sans-serif" font-size="11">{safe((item.get("album") or {}).get("name", "")[:55])}</text>',
        ]
    else:
        out += [
            '<rect x="28" y="120" width="138" height="138" rx="8" fill="#282828"/>',
            '<text x="97" y="190" text-anchor="middle" fill="#777777" font-family="Arial, sans-serif" font-size="14">♫</text>',
            '<text x="188" y="169" fill="#FFFFFF" font-family="Arial, sans-serif" font-size="23" font-weight="700">Nothing playing right now</text>',
            '<text x="188" y="198" fill="#B3B3B3" font-family="Arial, sans-serif" font-size="15">Your recent tracks are below.</text>',
        ]

    out += [
        '<line x1="28" y1="282" x2="772" y2="282" stroke="#303030"/>',
        '<text x="28" y="313" fill="#B3B3B3" font-family="Arial, sans-serif" font-size="13" font-weight="700" letter-spacing="1.5">LAST 3 TRACKS</text>',
    ]
    if not recent:
        out.append('<text x="28" y="350" fill="#B3B3B3" font-family="Arial, sans-serif" font-size="15">No recent tracks found.</text>')
    for i, entry in enumerate(recent[:3]):
        item = entry.get("track") or {}
        y = 333 + i * 53
        title = item.get("name", "Unknown track")
        artist = artists(item)
        link = (item.get("external_urls") or {}).get("spotify", "https://open.spotify.com/")
        art = get_art(item)
        if art:
            out.append(f'<image href="{safe(art)}" x="28" y="{y}" width="40" height="40" preserveAspectRatio="xMidYMid slice"/>')
        else:
            out.append(f'<rect x="28" y="{y}" width="40" height="40" rx="4" fill="#282828"/>')
        out += [
            f'<text x="84" y="{y+17}" fill="#FFFFFF" font-family="Arial, sans-serif" font-size="15" font-weight="600">{safe(title[:48])}</text>',
            f'<text x="84" y="{y+34}" fill="#B3B3B3" font-family="Arial, sans-serif" font-size="12">{safe(artist[:58])}</text>',
            f'<a href="{safe(link)}"><text x="765" y="{y+25}" text-anchor="end" fill="#1DB954" font-family="Arial, sans-serif" font-size="12">OPEN ↗</text></a>',
        ]
    out += [
        '<text x="772" y="496" text-anchor="end" fill="#666666" font-family="Arial, sans-serif" font-size="10">POWERED BY SPOTIFY WEB API</text>',
        '</svg>',
    ]
    return "\n".join(out)

def main():
    token = get_access_token()
    current = api_get("me/player/currently-playing", token)
    history = api_get("me/player/recently-played?limit=10", token) or {}
    recent = []
    seen = set()
    for entry in history.get("items", []):
        track = entry.get("track") or {}
        track_id = track.get("id") or track.get("name")
        if not track_id or track_id in seen:
            continue
        seen.add(track_id)
        recent.append(entry)
        if len(recent) == 3:
            break
    with open("spotify.svg", "w", encoding="utf-8") as f:
        f.write(render_svg(current, recent))
    print("Created spotify.svg")

if __name__ == "__main__":
    main()
