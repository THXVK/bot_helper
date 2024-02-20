import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from os import getenv
from data import channels, user_load, user_save
import random

load_dotenv()
token = getenv('TOKEN')
bot = telebot.TeleBot(token=token)


def gen_channels_markup(user_id):
    markup = InlineKeyboardMarkup()

    def gen_button(text, url):
        button = InlineKeyboardButton(text=text, url='https://t.me/' + url)
        markup.add(button)

    chosen_channels = random.choices(channels, k=3)

    users = user_load()

    for channel in chosen_channels:
        users[user_id]['channels'].append(
            {'name': list(channel.keys())[0], 'is_member': False, 'url': list(channel.values())[0]})
        for name, url in channel.items():
            gen_button(name, url)

    user_save(users)

    check_button = InlineKeyboardButton('проверить', callback_data='check')
    markup.add(check_button)
    return markup


@bot.message_handler(commands=['start'])
def start(message: Message):
    user_id = str(message.chat.id)
    users = user_load()

    users[user_id] = {
        "channels": [],
        "requests": []
    }
    user_save(users)

    bot.send_message(message.chat.id,
                     'Это телеграмм бот, предоставляющий уникальнейшую возможность пообщаться с Глебглобом')
    bot.send_message(message.chat.id, 'Чтобы начать, вам нужно подписаться на эти каналы:',
                     reply_markup=gen_channels_markup(user_id))


@bot.callback_query_handler(func=lambda call: call.data == 'check')
def check(call):
    user_id = str(call.message.chat.id)
    users = user_load()
    status = ['creator', 'administrator', 'member']
    for u_channel in users[user_id]['channels']:
        for i in status:
            if i == bot.get_chat_member(chat_id='@' + u_channel['url'], user_id=call.message.from_user.id):
                users[user_id]['channels'][u_channel]['is_member'] = True
                break

        else:
            bot.send_message(call.message.chat.id, f'вы еще не подписались на {u_channel["name"]}')
            break
    else:
        bot.send_message(call.message.chat.id, 'успех')


@bot.message_handler(content_types=['text'])
def register_user_request(message: Message):
    bot.send_message(message.chat.id, 'напишите свой запрос')


@bot.message_handler(content_types=['text'])
def echo(message: Message) -> None:
    """Функция ответа на некорректное сообщение от пользователя

    Функция отправляет сообщение с некорректным ответом от пользователя в формате
    'Вы напечатали: *сообщение пользователя*.что?'
    :param message: некорректное сообщение пользователя"""
    bot.send_message(chat_id=message.chat.id, text=f'Вы напечатали: {message.text}. Что?')


bot.infinity_polling()
