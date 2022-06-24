import json
import telebot
from downloader import *
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
token = os.getenv("TG_TOKEN")
bot = telebot.TeleBot(token, parse_mode=None)

users = {}


def update_users_write():
    with open('./users.json', 'w', encoding='UTF-8') as write_users:
        json.dump(users, write_users, ensure_ascii=False, indent=4)


def update_users_read():
    global users
    with open("./users.json", 'r', encoding='UTF-8') as read_users:
        users = json.load(read_users)


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


@bot.message_handler(commands=['start'])
def start(message):
    if str(message.from_user.id) in users.keys():
        pass
    elif str(message.from_user.id) not in users.keys():
        users[str(message.from_user.id)] = {
            "without_caption": 0
        }
        update_users_write()
    bot.reply_to(message, "Send me song name, son of bitch <3")


@bot.message_handler(commands=['help'])
def stop(message):
    bot.reply_to(message, "help urself))0)")


@bot.message_handler(commands=['stop'])
def stop(message):
    bot.reply_to(message, "ama unstoppable")


@bot.message_handler(commands=['switch_caption'])
def switch_caption(message):
    if users[str(message.from_user.id)]["without_caption"]:
        users[str(message.from_user.id)]["without_caption"] = 0
        bot.send_message(message.chat.id, "Caption enabled")
    else:
        users[str(message.from_user.id)]["without_caption"] = 1
        bot.send_message(message.chat.id, "Caption disabled")
    update_users_write()


@bot.message_handler(func=lambda m: True)
def msg_handler(message):
    song_name = message.text
    markup = get_songs_list_markup(message, song_name, 1)
    if markup:
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
        caption = "[via](https://t.me/lyp1noff_music_bot)"
        if users[str(call.from_user.id)]["without_caption"]:
            caption = ""
        bot.send_audio(message.chat.id, audio, caption=caption,
                       title=song_name, performer=song_artist, parse_mode="MarkdownV2")
    else:
        print("wrong callback data")


if __name__ == '__main__':
    update_users_read()
    print("Started")
    bot.infinity_polling()
