import json
import sqlite3

settings_dict = {
    'subject': [
        'Русский',
        'Математика'
    ],
    'difficulty': [
        'новичок',
        'любитель',
        'профи'
    ]
}
filename_1 = '../bot_helper/users_data.json'


def user_load() -> dict:
    try:
        with open(filename_1, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def user_save(data: dict):
    with open(filename_1, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


connection = sqlite3.connect('sqlite3.db', check_same_thread=False)
cur = connection.cursor()

channels = {
    "'канал 1'": 'derteafg',
    "'канал 2'": 'SDFWDGW',
    "'канал 3'": 'sdfsadfsdeq',
    "'канал 4'": 'sertsdfgWS',
}

cur.execute('''CREATE TABLE IF NOT EXISTS channels (
                            url TEXT PRIMARY KEY,
                            channel_name TEXT
                       );''')

for channel in channels.items():
    try:
        q = f'SELECT * FROM channels WHERE url = {channel[1]}'
        r = cur.execute(q)
    except sqlite3.OperationalError:
        cur.execute('''INSERT INTO channels (url, channel_name)
                        VALUES (?, ?)''', (channel[1], channel[0]))

connection.commit()

connection.row_factory = sqlite3.Row
cur = connection.cursor()


def get_table_data(table):
    q = f'SELECT * FROM {table};'
    table_data = cur.execute(q)
    return table_data


def normal(table_data):
    result = []
    for data in table_data:
        result.append(data)
    return result


connection.close()
