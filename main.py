import requests
from bs4 import BeautifulSoup

def search_song(song_name, page_num):
    search_url = "https://downloadmusicvk.ru/audio/search?q={}&page={}".format(song_name, page_num)
    r = requests.get(search_url)

    soup = BeautifulSoup(r.text, "html.parser")
    songs_list_raw = soup.findAll('div', class_='row audio vcenter')
    songs_list = []
    for data in songs_list_raw:
        if data.find('a') is not None:
            song_name_raw = data.text
            song_name = song_name_raw.replace("\n", "")

            data = str(data)
            song_data = data[data.find('data-model="')+12:data.find('">')]

            songs_list.append([song_name, song_data])
    return songs_list


def download_song(song_name, song_data):
    r = requests.get("https://downloadmusicvk.ru/audio/play?data={}".format(song_data))
    name = "{}.mp3".format(song_name[:song_name.find("  ")])
    with open(name, 'wb') as f:
        f.write(r.content)
    return name


def main():
    song_name = "просыпайся zoo in space"
    page_num = 1
    songs_list = search_song(song_name, page_num)
    download_song(songs_list[0][0], songs_list[0][1])

if __name__ == '__main__':
    main()
