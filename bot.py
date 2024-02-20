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
        users = user_load()
        users[user_id]['channels'][list(channel.keys())[0]] = {'name': list(channel.keys())[0],
                                                               'is_member': False, 'url': list(channel.values())[0]}
        user_save(users)
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
        "channels": {},
        "requests": []
    }
    user_save(users)

    bot.send_message(message.chat.id,
                     'Это телеграмм бот, предоставляющий уникальнейшую возможность пообщаться с Глебглобом')
    msg = bot.send_message(message.chat.id, 'Чтобы начать, вам нужно подписаться на эти каналы:',
                           reply_markup=gen_channels_markup(user_id))
    bot.register_next_step_handler(msg, access_denied)


def access_denied(message):
    users = user_load()
    user_id = str(message.chat.id)
    for channel in users[user_id]['channels']:
        if not users[user_id]['channels'][channel]['is_member']:
            msg = bot.send_message(message.chat.id, 'прежде чем что-то сделать, вы должны пройти проверку')
            bot.register_next_step_handler(msg, access_denied)


@bot.callback_query_handler(func=lambda call: call.data == 'check')
def check(call):
    user_id = str(call.message.chat.id)
    users = user_load()
    status = ['creator', 'administrator', 'member']
    for u_channel in users[user_id]['channels']:
        for i in status:
            if i == bot.get_chat_member(chat_id='@' + users[user_id]['channels'][u_channel]['url'],
                                        user_id=call.message.from_user.id).status:
                users[user_id]['channels'][u_channel]['is_member'] = True
                break
        else:
            user_save(users)
            bot.send_message(call.message.chat.id, f'вы еще не подписались на {u_channel["name"]}')
            break
    else:
        user_save(users)
        bot.send_message(call.message.chat.id, 'вы прошли проверку')
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        first_user_request(call.message.chat.id)


def first_user_request(chat_id):
    msg = bot.send_message(chat_id, 'напишите свой запрос')
    bot.register_next_step_handler(msg, register_user_request)


def status_check(message):
    users = user_load()
    user_id = str(message.chat.id)
    for channel in users[user_id]['channels']:
        if not users[user_id]['channels'][channel]['is_member']:
            bot.send_message(message.chat.id, 'вы подписаны не на все каналы')
            break


@bot.message_handler(content_types=['text'], func=status_check)
def register_user_request(message: Message):
    bot.send_message(message.chat.id, f'ваш запрос: {message.text}')
    ...


...


@bot.message_handler(content_types=['text'])
def echo(message: Message) -> None:
    """Функция ответа на некорректное сообщение от пользователя

    Функция отправляет сообщение с некорректным ответом от пользователя в формате
    'Вы напечатали: *сообщение пользователя*.что?'
    :param message: некорректное сообщение пользователя"""
    bot.send_message(chat_id=message.chat.id, text=f'Вы напечатали: {message.text}. Что?')


bot.infinity_polling()