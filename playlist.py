import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Replace with your Spotify credentials
CLIENT_ID = "16d4294cce4044ba9e67f2ada8372f76"
CLIENT_SECRET = "f2a156c5de284a5b9a5e8475648b4ff5"
REDIRECT_URI = "http://localhost:8888/callback"

# Define required scopes
SCOPE = "user-modify-playback-state user-read-playback-state user-read-currently-playing"

# Authenticate
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

# Get user's devices (make sure Spotify is open on your device)
devices = sp.devices()
device_id = None
if devices['devices']:
    device_id = devices['devices'][0]['id']  # Use the first available device




playlist_ask =  input('what do you wanna play ')

playlist_fuck_it = "spotify:playlist:06Aun3V4PIAkeLJ0xttfQr?si=64e22a7627324eb6"
playlist_studying = "https://open.spotify.com/playlist/37i9dQZF1DX8Uebhn9wzrS?si=4492546c1ae744f8"
playlist_pre_game = "https://open.spotify.com/playlist/0xt1PpIkKcydgR6gZJ2t9P?si=a176dcaea4dd4f8e"


def playlist_play(playlist):
    sp.start_playback(device_id=device_id, context_uri= playlist)
    print("Playing playlist...")

if 'fuck it' in playlist_ask:
    playlist_play(playlist_fuck_it)
elif 'study music' in playlist_ask:
    playlist_play(playlist_studying)
elif ' pre game' in playlist_ask:
    playlist_play(playlist_pre_game)