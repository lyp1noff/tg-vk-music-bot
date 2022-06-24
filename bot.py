import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from downloader import *

song_name = ''
songs_list = []

bot = telebot.TeleBot(
    "5450349606:AAHJ4VszZPLqZQHksgGX1iIXT3wzFQXFW1M", parse_mode=None)


def get_songs_list_markup(message, song_name, page_num):
    global songs_list
    try:
        songs_list = search_song(song_name, page_num)
    except Exception:
        bot.send_message(message.chat.id, "retarded...")
    if not songs_list:
        bot.send_message(message.chat.id, "not found(")
        return

    markup = InlineKeyboardMarkup()
    for song_id, song in enumerate(songs_list):
        markup.add(InlineKeyboardButton(
            song[0], callback_data="dwnldsong{}".format(song_id)))
    if page_num > 1:
        markup.add(InlineKeyboardButton("<", callback_data="page_prev{}".format(page_num)),
                   InlineKeyboardButton(">", callback_data="page_next{}".format(page_num)))
    else:
        markup.add(InlineKeyboardButton(
            ">", callback_data="page_next{}".format(page_num)))
    return markup


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Send me song name, son of bitch <3")


@bot.message_handler(func=lambda m: True)
def msg_handler(message):
    global song_name
    song_name = message.text
    markup = get_songs_list_markup(message, song_name, 1)
    bot.send_message(message.chat.id, "Choose one of 'em", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    message = call.message
    if "page_prev" in call.data:
        page_num = int(call.data[9:]) - 1
        markup = get_songs_list_markup(message, song_name, page_num)
        bot.edit_message_text(
            "Choose one of 'em", message.chat.id, message.id, reply_markup=markup)
    elif "page_next" in call.data:
        page_num = int(call.data[9:]) + 1
        markup = get_songs_list_markup(message, song_name, page_num)
        bot.edit_message_text(
            "Choose one of 'em", message.chat.id, message.id, reply_markup=markup)
    elif "dwnldsong" in call.data:
        bot.answer_callback_query(call.id, "downloading")
        song_id = int(call.data[9:])
        filename = download_song(songs_list[song_id][0], songs_list[song_id][1])
        audio = open('songs/{}'.format(filename), 'rb')
        bot.send_audio(message.chat.id, audio)


if __name__ == '__main__':
    bot.infinity_polling()