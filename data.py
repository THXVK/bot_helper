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


connection = sqlite3.connect('sqlite3.db')
cur = connection.cursor()

channels = {
    "'канал 1'": 'derteafg',
    "'канал 2'": 'SDFWDGW',
    "'канал 3'": 'sdfsadfsdeq',
    "'канал 4'": 'sertsdfgWS',
}

cur.execute('''CREATE TABLE IF NOT EXISTS channels (
                            channel_name TEXT PRIMARY KEY,
                            url TEXT
                       );''')

for channel in channels.items():
    print(channel[0])
    q = f'SELECT * FROM channels WHERE channel_name = {channel[0]}'
    if not cur.execute(q):
        cur.execute('''INSERT INTO channels (channel_name, url)
                        VALUES (?, ?)''', (channel[0], channel[1]))

connection.commit()
