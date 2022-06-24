import telebot
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from downloader import *

load_dotenv()
token = os.getenv("TG_TOKEN")
bot = telebot.TeleBot(token, parse_mode=None)


def get_songs_list_markup(message, song_req, page_num):
    songs_list = []
    try:
        songs_list = search_song(song_req, page_num)
    except Exception:
        bot.send_message(message.chat.id, "retarded...")
    if not songs_list:
        bot.send_message(message.chat.id, "not found(")
        return

    markup = InlineKeyboardMarkup()
    for song_page_id, song in enumerate(songs_list):
        markup.add(InlineKeyboardButton(
            song[0], callback_data="dwnldsong|{}|{}|{}".format(page_num, song_req, song_page_id)))
    markup.add(InlineKeyboardButton("<", callback_data="page_prev|{}|{}".format(page_num, song_req)),
               InlineKeyboardButton("X", callback_data="delmsg"),
               InlineKeyboardButton(">", callback_data="page_next|{}|{}".format(page_num, song_req)))
    return markup


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Send me song name, son of bitch <3")


@bot.message_handler(func=lambda m: True)
def msg_handler(message):
    song_name = message.text
    markup = get_songs_list_markup(message, song_name, 1)
    bot.send_message(message.chat.id, "Choose one of 'em", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    message = call.message
    data = str(call.data).split("|")
    if "page" in data[0]:
        page_num = int(data[1])
        song_req = data[2]
        if data[0] == "page_prev":
            if page_num - 1 >= 1:
                markup = get_songs_list_markup(message, song_req, page_num - 1)
                bot.edit_message_text(
                    "Choose one of 'em", message.chat.id, message.id, reply_markup=markup)
            else:
                bot.answer_callback_query(call.id, "it's already first page -_-")
        elif data[0] == "page_next":
            markup = get_songs_list_markup(message, song_req, page_num + 1)
            bot.edit_message_text(
                "Choose one of 'em", message.chat.id, message.id, reply_markup=markup)
    elif data[0] == "delmsg":
        bot.delete_message(message.chat.id, message.id)
    elif data[0] == "dwnldsong":
        page_num = int(data[1])
        song_req = data[2]
        song_page_id = int(data[3])
        bot.answer_callback_query(call.id, "downloading")
        songs_list = search_song(song_req, page_num)
        filename = download_song(songs_list[song_page_id][0], songs_list[song_page_id][1])
        audio = open('./songs/{}'.format(filename), 'rb')
        song_name_full = filename[:-4]
        song_name = song_name_full[song_name_full.find(' - ') + 3:]
        song_artist = song_name_full[:song_name_full.find(' - ')]
        bot.send_audio(message.chat.id, audio, title=song_name, performer=song_artist)
    else:
        print("wrong callback data")


if __name__ == '__main__':
    print("Started")
    bot.infinity_polling()
