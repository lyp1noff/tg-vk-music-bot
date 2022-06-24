import eyed3
import requests
from bs4 import BeautifulSoup


def search_song(song_name, page_num):
    search_url = "https://downloadmusicvk.ru/audio/search?q={}&page={}".format(
        song_name, page_num)
    r = requests.get(search_url)

    soup = BeautifulSoup(r.text, "html.parser")
    songs_list_raw = soup.findAll('div', class_='row audio vcenter')
    songs_list = []
    for data in songs_list_raw:
        if data.find('a') is not None:
            song_name_raw = data.text
            song_name = song_name_raw.replace("\n", "")

            data = str(data)
            song_data = data[data.find('data-model="') + 12:data.find('">')]

            songs_list.append([song_name, song_data])
    return songs_list


def download_song(song_name, song_data):
    r = requests.get(
        "https://downloadmusicvk.ru/audio/play?data={}".format(song_data))
    song_name_full = song_name[:song_name.find("  ")]
    filename = "{}.mp3".format(song_name_full)
    with open("songs/{}".format(filename), 'wb') as f:
        f.write(r.content)

    song_name = song_name_full[song_name_full.find(' - ') + 3:]
    song_artist = song_name_full[:song_name_full.find(' - ')]
    
    audiofile = eyed3.load("songs/{}".format(filename))
    audiofile.tag.title = song_name
    audiofile.tag.artist = song_artist
    # audiofile.tag.album = "Free For All Comp LP"
    # audiofile.tag.album_artist = "Various Artists"
    audiofile.tag.save()
    
    return filename
