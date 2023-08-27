import spotipy, ffmpeg, os, re
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube
from pytube import Search
import PySimpleGUI as sg
import threading as th


client_id = "11c85887b3b84bebb1d123fcac478478"
client_secret = "8a0d1a1bedc24696ae4a152d477391bd"

# Authenticate with the Spotify API using client credentials
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Get the playlist object from the Spotify API
def download_playlist(playlist_uri, progress_bar):
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
        progress_bar.UpdateBar(i+1, len(song_names))

    sg.Popup('Download complete! The songs are saved on downloads.', title='Success')

layout = [[sg.Text('Playlist/Album link ->'), sg.InputText()],
          [sg.ProgressBar(100, orientation='h', size=(20, 20), key='progressbar'), sg.Button('Start', button_color=('white', 'black'), bind_return_key=True, disabled=False)]]

window = sg.Window('My GUI', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Start':
        input_text = values[0]
        # Do something with the input text here
        print(f"Starting with input: {input_text}")

        # Remove the "si" parameter from the URL
        input_text = input_text.replace("intl-es/", "")

        pattern = r'(playlist|album)/([a-zA-Z0-9]+)'

        # Use re.search to find the match in the URL
        match = re.search(pattern, input_text)

        # Check if a match is found
        if match:
            # Extract the playlist/album ID from the match object
            playlist_id = match.group(2)
            print("Playlist/Album ID:", playlist_id)
            progress_bar = window['progressbar']
            if "playlist" in input_text:
                progress_bar.UpdateBar(0, len(sp.playlist_tracks(playlist_id)['items']))
            elif "album" in input_text:
                progress_bar.UpdateBar(0, len(sp.album_tracks(playlist_id)['items']))
            window['Start'].update(disabled=True, button_color=('white', 'grey'))
            download_thread = th.Thread(target=download_playlist, args=(input_text, progress_bar))
            download_thread.start()
        else:
            print("No playlist/album ID found in the URL.")

window.close()