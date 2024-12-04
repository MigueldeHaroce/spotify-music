import spotipy, ffmpeg, os, re, requests, urllib.request
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube
from pytube import Search
import PySimpleGUI as sg
import threading as th

from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3

client_id = ""
client_secret = ""

# Authenticate with the Spotify API using client credentials
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Get the playlist object from the Spotify API
def download_playlist(playlist_uri, progress_bar):
    try:
        if "playlist" in playlist_uri:
            playlist = sp.playlist(playlist_uri)
            track_info = get_playlist_info(playlist_uri)
            song_names = [f'{track["track"]["name"]} - {track["track"]["artists"][0]["name"]} audio' for track in playlist["tracks"]["items"]]
            print(song_names)
        elif "album" in playlist_uri:
            playlist = sp.album(playlist_uri)
            track_info = get_album_info(playlist_uri) # TODO: Implement get_album_info
            song_names = [f'{track["name"]} - {track["artists"][0]["name"]} audio' for track in album["tracks"]["items"]]
        else:
            print("Invalid URL. Please provide a valid playlist or album URL.")
            return
    except spotipy.SpotifyException as e:
        print(f"Error: {e}")
        exit()

    # Create a folder with the name of the playlist/album on the desktop
    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    playlist_name = playlist["name"] if "playlist" in playlist_uri else album["name"]
    for char in invalid_chars:
        playlist_name = playlist_name.replace(char, '')
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    output_path = os.path.join(desktop_path, playlist_name)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for i, song in enumerate(song_names):
        try:
            video_link = find_youtube(song)
            video = YouTube(video_link)
            stream = video.streams.filter(only_audio=True).first()
            print(f'Downloading audio: {video.title}')
            stream.download(output_path=output_path)
            input_file = ffmpeg.input(f'{output_path}/{stream.default_filename}')
            output_file = input_file.output(f'{output_path}/{song}.mp3')
            ffmpeg.run(output_file)
            os.remove(f'{output_path}/{stream.default_filename}')

            set_metadata(track_info, f'{output_path}/{song}.mp3', i)

        except Exception as e:
            print(f"Error: {e} occurred while downloading {song}.")
            continue

        progress_bar.UpdateBar(i+1, len(song_names))

    sg.Popup('Download complete! The songs are saved on downloads.', title='Success')

def find_youtube(query):
    phrase = query.replace(" ", "+")
    search_link = "https://www.youtube.com/results?search_query=" + phrase
    count = 0
    while count < 5:
        try:
            response = urllib.request.urlopen(search_link)
            search_results = re.findall(r"watch\?v=(\S{11})", response.read().decode())
            first_vid = "https://www.youtube.com/watch?v=" + search_results[count]
            tryvideo = YouTube(first_vid)
            stream = tryvideo.streams.filter(only_audio=True).first()
            break
        except:
            count += 1
            print("Retrying... aaaaaaaaaaaaaaaaaaaaaaaaaaa")
    else:
        raise ValueError("Please check your internet connection and try again later.")




    return first_vid

def get_track_info(track_url):

    track = sp.track(track_url)

    track_metadata = {
        "artist_name": track["artists"][0]["name"],
        "track_title": track["name"],
        "track_number": track["track_number"],
        "isrc": track["external_ids"]["isrc"],
        "album_art": track["album"]["images"][1]["url"],
        "album_name": track["album"]["name"],
        "release_date": track["album"]["release_date"],
        "artists": [artist["name"] for artist in track["artists"]],
    }

    return track_metadata

def get_playlist_info(sp_playlist):

    playlist = sp.playlist_tracks(sp_playlist)

    tracks = [item["track"] for item in playlist["items"]]
    tracks_info = []
    for track in tracks:
        track_url = f"https://open.spotify.com/track/{track['id']}"
        track_info = get_track_info(track_url)
        tracks_info.append(track_info)

    return tracks_info

def set_metadata(metadata, file_path, count_song):

    mp3file = EasyID3(file_path)

    # add metadata
    mp3file["albumartist"] = metadata[count_song]["artist_name"]
    mp3file["artist"] = metadata[count_song]["artists"]
    mp3file["album"] = metadata[count_song]["album_name"]
    mp3file["title"] = metadata[count_song]["track_title"]
    mp3file["date"] = metadata[count_song]["release_date"]
    mp3file["tracknumber"] = str(metadata[int(count_song)]["track_number"])
    mp3file["isrc"] = metadata[count_song]["isrc"]
    mp3file.save()

    # add album cover
    audio = ID3(file_path)
    with urllib.request.urlopen(metadata[count_song]["album_art"]) as albumart:
        audio["APIC"] = APIC(
            encoding=3, mime="image/jpeg", type=3, desc="Cover", data=albumart.read()
        )
    audio.save(v2_version=3)

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
