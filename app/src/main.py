import spotipy, ffmpeg, os, re
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube
from pytube import Search
import threading as th
import json

# Do something with inputValue

client_id = "11c85887b3b84bebb1d123fcac478478"
client_secret = "8a0d1a1bedc24696ae4a152d477391bd"

# Authenticate with the Spotify API using client credentials
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Get the playlist object from the Spotify API
def download_playlist(playlist_uri):
    try:
        if "playlist" in playlist_uri:
            playlist = sp.playlist(playlist_uri)
            song_names = [f'{track["track"]["name"]} - {track["track"]["artists"][0]["name"]}' for track in playlist["tracks"]["items"]]
        elif "album" in playlist_uri:
            album = sp.album(playlist_uri)
            song_names = [f'{track["name"]} - {track["artists"][0]["name"]}' for track in album["tracks"]["items"]]
        else:
            print("Invalid URL. Please provide a valid playlist or album URL.")
            return
    except spotipy.SpotifyException as e:
        print(f"Error: {e}")
        exit()

    # Create a folder with the name of the playlist/album on the desktop
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads')
    playlist_name = os.path.join(desktop_path, playlist["name"] if "playlist" in playlist_uri else album["name"])
    if not os.path.exists(playlist_name):
        os.makedirs(playlist_name)

    for i, song in enumerate(song_names):
        try:
            search = Search(song)
            video = search.results[0]
            print(f'Downloading audio: {video.title}')
            stream = video.streams.filter(only_audio=True).first()
            if stream is None:
                print(f"Error: {song} cannot be downloaded due to age restriction or other reasons.")
                continue
            stream.download(output_path=playlist_name)
            input_file = ffmpeg.input(f'{playlist_name}/{stream.default_filename}')
            output_file = input_file.output(f'{playlist_name}/{song}.mp3')
            ffmpeg.run(output_file)
            os.remove(f'{playlist_name}/{stream.default_filename}')
        except Exception as e:
            print(f"Error: {e} occurred while downloading {song}.")


download_playlist(input_value)
