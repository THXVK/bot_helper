import telebot
import random
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from data import settings_dict, get_table_data, is_user_in_table, add_new_user, get_user_data, update_row_questions, \
    update_row_subscribe
from gpt import gpt_dialog
from config import token

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


@bot.message_handler(commands=['start'])
def start(message: Message):
    user_id = message.chat.id

    if not is_user_in_table(user_id, 'users_questions_data'):
        channels = get_table_data('channels')
        markup = InlineKeyboardMarkup()
        chosen_channels = random.sample(channels, k=3)
        user = get_user_data(user_id, 'users_subscribe_data')

        def gen_button(text, url):
            button = InlineKeyboardButton(text=text, url='https://t.me/' + url)
            markup.add(button)

        for channel in chosen_channels:
            name = channel[1]
            url = channel[0]

            if not user or len(user) < 3:
                add_new_user((user_id, name, url, 0),
                             'users_subscribe_data',
                             ['user_id', 'channel_name', 'url', 'is_member'])

            gen_button(name, url)

        check_button = InlineKeyboardButton('проверить', callback_data='check')
        markup.add(check_button)

        bot.send_message(message.chat.id,
                         'Это телеграмм бот - помощник')
        msg = bot.send_message(message.chat.id, 'Чтобы начать, вам нужно подписаться на эти каналы:',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, access_denied)
    elif status_check(message):
        bot.send_message(message.chat.id, 'вы уже прошли проверку')
        actions_1(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'вы все еще не подписаны на каналы')


def access_denied(message):
    user_id = message.chat.id
    user = get_user_data(user_id, 'users_subscribe_data')
    for i in user:
        if not i[4]:
            msg = bot.send_message(message.chat.id, 'прежде чем что-то сделать, вы должны пройти проверку')
            bot.register_next_step_handler(msg, access_denied)
            break


@bot.callback_query_handler(func=lambda call: call.data == 'check')
def check(call):
    user_id = call.message.chat.id
    user = get_user_data(user_id, 'users_subscribe_data')
    status = ['creator', 'administrator', 'member']

    for i in user:
        u_channel = i[2]

        if bot.get_chat_member(chat_id='@' + i[3],
                               user_id=call.message.chat.id).status in status:
            update_row_subscribe(user_id, 'is_member', i[3], 1, 'users_subscribe_data')
        else:
            bot.send_message(call.message.chat.id, f'вы еще не подписались на {u_channel}')
            break
    else:
        add_new_user((user_id, '', '', '', ''),
                     'users_questions_data',
                     ['user_id', 'subject', 'difficulty', 'question', 'answer'])

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'вы прошли проверку')
        settings_choice_1(call.message.chat.id)


def settings_choice_1(chat_id):
    bot.send_message(chat_id, 'выберите тему:', reply_markup=gen_settings_markup('subject'))


def settings_choice_2(chat_id):
    bot.send_message(chat_id, 'выберите сложность:', reply_markup=gen_settings_markup('difficulty'))


@bot.callback_query_handler(func=lambda call: call.data.endswith('set'))
def settings_change(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    chat_id = call.message.chat.id
    user_id = chat_id
    user_data = get_user_data(user_id, 'users_questions_data')[0]

    param = call.data.split('_')[0]
    set = call.data.split('_')[1]

    if set == 'subject':
        set_index = 2
    else:
        set_index = 3

    if user_data[set_index]:
        add_new_user((user_id, '', '', '', ''),
                     'users_questions_data',
                     ['user_id', 'subject', 'difficulty', 'question', 'answer'])
    else:
        update_row_questions(user_id, set, param, 'users_questions_data')

    bot.send_message(chat_id, 'настройки изменены')
    actions_1(chat_id)


def actions_1(chat_id):
    user_id = chat_id
    user = get_user_data(user_id, 'users_questions_data')[0]

    # если новый пользователь без предмета
    if not user[2] and len(get_user_data(user_id, 'users_questions_data')) == 1:
        settings_choice_1(chat_id)

    # если новый пользователь без сложности
    elif not user[3] and len(get_user_data(user_id, 'users_questions_data')) == 1:
        settings_choice_2(chat_id)

    # если старый пользователь без предмета
    elif not user[2]:
        sub = get_user_data(user_id, 'users_questions_data')[1][2]  # настройка из предыдущего запроса
        update_row_questions(user_id, 'subject', sub, 'users_questions_data')
        actions_1(chat_id)

    # если старый пользователь без сложности
    elif not user[3]:
        diff = get_user_data(user_id, 'users_questions_data')[1][3]
        update_row_questions(user_id, 'difficulty', diff, 'users_questions_data')
        actions_1(chat_id)

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
    user = get_user_data(chat_id, 'users_questions_data')[0]
    sub = user[2]
    diff = user[3]

    if user[4]:
        add_new_user((chat_id, sub, diff, '', ''),
                     'users_questions_data',
                     ['user_id', 'subject', 'difficulty', 'question', 'answer'])

    msg = bot.send_message(chat_id, 'напишите свой запрос:')
    bot.register_next_step_handler(msg, register_user_request)


def status_check(message):
    user_id = message.chat.id
    user = get_user_data(user_id, 'users_subscribe_data')

    for i in user:
        if not i[4]:
            bot.send_message(message.chat.id, f'вы не подписаны на {i[2]}')
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
        user_id = message.chat.id
        user_request = message.text

        update_row_questions(user_id, 'question', user_request, 'users_questions_data')
        answer = gpt_dialog(user_request, user_id)
        update_row_questions(user_id, 'answer', answer, 'users_questions_data')
        bot.send_message(message.chat.id, answer)
        first_user_request(message.chat.id)

    elif message.text == '/stop':
        bot.send_message(message.chat.id, 'сессия приостановлена, чтобы ее продолжить, напишите /continue')

    else:
        bot.send_message(message.chat.id,
                         'чтобы использовать команды, вы должны приостановить этот высокоинтеллектуальный диалог, /stop?')
        first_user_request(message.chat.id)


bot.infinity_polling()
