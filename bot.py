import telebot
import random
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from os import getenv
from data import user_load, user_save, settings_dict, get_table_data, normal
from gpt import gpt_dialog

load_dotenv()
token = getenv('TOKEN')
bot = telebot.TeleBot(token=token)


@bot.message_handler(commands=['help'])
def help(message: Message):
    bot.send_message(message.chat.id, """
/start - команда для запуска бота
/help - список команд
/stop - остановка диалога
/continue - продолжение диалога
    """)


@bot.message_handler(commands=['settings'])
def settings(message: Message):
    actions_1(message.chat.id)


@bot.message_handler(commands=['continue'])
def continue_session(message):
    first_user_request(message.chat.id)


@bot.message_handler(commands=['debug'])
def debug(message):
    with open('other/logConfig.log', 'rb') as file:
        f = file.read()
    bot.send_document(message.chat.id, f, visible_file_name='other/logConfig.log')


def gen_settings_markup(settings):
    markup = InlineKeyboardMarkup()

    def gen_button(text, callback):
        button = InlineKeyboardButton(text=text, callback_data=callback + '_' + settings + '_set')
        markup.add(button)

    for param in settings_dict[settings]:
        gen_button(param, param)

    return markup


def gen_channels_markup(user_id):
    channels_data = get_table_data('channels')
    channels = normal(channels_data)
    markup = InlineKeyboardMarkup()

    def gen_button(text, url):
        button = InlineKeyboardButton(text=text, url='https://t.me/' + url)
        markup.add(button)

    chosen_channels = random.sample(channels, k=3)

    users = user_load()

    for channel in chosen_channels:
        users = user_load()
        users[user_id]['channels'][channel['channel_name']] = {'name': channel['channel_name'],
                                                               'is_member': False, 'url': channel['url']}
        user_save(users)
        name = channel['channel_name']
        url = channel['url']
        gen_button(name, url)

    user_save(users)

    check_button = InlineKeyboardButton('проверить', callback_data='check')
    markup.add(check_button)
    return markup


@bot.message_handler(commands=['start'])
def start(message: Message):
    user_id = str(message.chat.id)
    users = user_load()
    if user_id not in users:
        users[user_id] = {
            "channels": {},
            "requests": [],
            "settings": {"difficulty": "",
                         "subject": ""
                         }
        }
        user_save(users)

        bot.send_message(message.chat.id,
                         'Это телеграмм бот - помощник')
        msg = bot.send_message(message.chat.id, 'Чтобы начать, вам нужно подписаться на эти каналы:',
                               reply_markup=gen_channels_markup(user_id))
        bot.register_next_step_handler(msg, access_denied)
    elif status_check(message):
        bot.send_message(message.chat.id, 'вы уже прошли проверку')
        first_user_request(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'вы все еще не подписаны')


def access_denied(message):
    users = user_load()
    user_id = str(message.chat.id)
    for channel in users[user_id]['channels']:
        if not users[user_id]['channels'][channel]['is_member']:
            msg = bot.send_message(message.chat.id, 'прежде чем что-то сделать, вы должны пройти проверку')
            bot.register_next_step_handler(msg, access_denied)
            break


@bot.callback_query_handler(func=lambda call: call.data == 'check')
def check(call):
    user_id = str(call.message.chat.id)
    users = user_load()
    status = ['creator', 'administrator', 'member']
    for u_channel in users[user_id]['channels']:

        if bot.get_chat_member(chat_id='@' + users[user_id]['channels'][u_channel]['url'],
                               user_id=call.message.chat.id).status in status:
            users[user_id]['channels'][u_channel]['is_member'] = True

        else:
            user_save(users)
            bot.send_message(call.message.chat.id, f'вы еще не подписались на {u_channel}')
            break
    else:
        user_save(users)
        bot.send_message(call.message.chat.id, 'вы прошли проверку')
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        settings_choice_1(call.message.chat.id)


def settings_choice_1(chat_id):
    bot.send_message(chat_id, 'выберите тему:', reply_markup=gen_settings_markup('subject'))


def settings_choice_2(chat_id):
    bot.send_message(chat_id, 'выберите сложность:', reply_markup=gen_settings_markup('difficulty'))


@bot.callback_query_handler(func=lambda call: call.data.endswith('set'))
def settings_change(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    chat_id = call.message.chat.id
    user_id = str(chat_id)
    users = user_load()
    param = call.data.split('_')[0]
    set = call.data.split('_')[1]

    users[user_id]['settings'][set] = param
    user_save(users)
    bot.send_message(chat_id, 'настройки изменены')
    actions_1(chat_id)


def actions_1(chat_id):
    user_id = str(chat_id)
    users = user_load()
    if not users[user_id]['settings']['difficulty']:
        settings_choice_2(chat_id)
    elif not users[user_id]['settings']['subject']:
        settings_choice_1(chat_id)
    else:
        actions_markup = InlineKeyboardMarkup()
        button_1 = InlineKeyboardButton(text='сменить тему', callback_data='sub_action')
        button_2 = InlineKeyboardButton(text='сменить сложность', callback_data='diff_action')
        button_3 = InlineKeyboardButton(text='задать вопрос', callback_data='ask_action')
        actions_markup.add(button_1, button_2, button_3, row_width=2)

        bot.send_message(chat_id, 'что вы хотите сделать?', reply_markup=actions_markup)


@bot.callback_query_handler(func=lambda call: call.data.endswith('action'))
def actions_2(call):
    chat_id = call.message.chat.id
    action = call.data.split('_')[0]
    bot.delete_message(chat_id, call.message.message_id)

    if action == 'ask':
        first_user_request(chat_id)
    elif action == 'sub':
        settings_choice_1(chat_id)
    else:
        settings_choice_2(chat_id)


def first_user_request(chat_id):
    msg = bot.send_message(chat_id, 'напишите свой запрос:')
    bot.register_next_step_handler(msg, register_user_request)


def status_check(message):
    users = user_load()
    user_id = str(message.chat.id)
    for channel in users[user_id]['channels']:
        if not users[user_id]['channels'][channel]['is_member']:
            bot.send_message(message.chat.id, 'вы подписаны не на все каналы')
            return False
    return True


@bot.message_handler(content_types=['text'])
def echo(message: Message) -> None:
    """Функция ответа на некорректное сообщение от пользователя

    Функция отправляет сообщение с некорректным ответом от пользователя в формате
    'Вы напечатали: *сообщение пользователя*.что?'
    :param message: некорректное сообщение пользователя"""
    bot.send_message(chat_id=message.chat.id, text=f'Вы напечатали: {message.text}. Что?')


@bot.message_handler(content_types=['text'], func=status_check)
def register_user_request(message: Message):
    if not message.text.startswith('/'):

        users = user_load()
        user_id = str(message.chat.id)
        user_request = message.text

        ...

        users[user_id]['requests'].append(message.text)
        user_save(users)

        bot.send_message(message.chat.id, gpt_dialog(user_request, user_id))
        first_user_request(message.chat.id)

    elif message.text == '/stop':
        bot.send_message(message.chat.id, 'сессия приостановлена, чтобы ее продолжить, напишите /continue')

    else:
        bot.send_message(message.chat.id,
                         'чтобы использовать команды, вы должны приостановить этот высокоинтеллектуальный диалог, /stop?')
        first_user_request(message.chat.id)


bot.infinity_polling()
