import json
import sqlite3

DB_NAME = 'sqlite3.db'

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


channels = {
    'канал 1': 'derteafg',
    'канал 2': 'SDFWDGW',
    'канал 3': 'sdfsadfsdeq',
    'канал 4': 'sertsdfgWS',
}


#    "channels": {},
#    "requests": [],
#   "settings": {"difficulty": "",
#               "subject": ""
#              }


def execute_query(query: str, data: tuple | None = None, db_name: str = DB_NAME):
    try:
        connection = sqlite3.connect(db_name, check_same_thread=False)
        cursor = connection.cursor()

        if data:
            cursor.execute(query, data)
            connection.commit()
        else:
            cursor.execute(query)

    except sqlite3.Error as e:
        return e

    else:
        result = cursor.fetchall()
        connection.close()
        return result


def add_new_user(users_data: tuple, table: str, columns: list):
    if not is_user_in_table(users_data[0], table):
        sql_query = (
            f'INSERT INTO {table} '
            f'({', '.join(columns)}) '
            f'VALUES ({'?, ' * (len(columns) - 1) + '?'});')
        execute_query(sql_query, users_data)
        return True
    else:
        return False


def is_user_in_table(user_id: int, table: str) -> bool:
    sql_query = (
        f'SELECT * '
        f'FROM {table} '
        f'WHERE user_id = ?;'
    )
    return bool(execute_query(sql_query, (user_id,)))


def update_row(user_id: int, column_name: str, new_value: str, table: str):
    if is_user_in_table(user_id, table):
        sql_query = (
            f'update {table} '
            f'SET {column_name} = ? '
            f'WHERE user_id = ?;'
        )

        execute_query(sql_query, (new_value, user_id))
        return True
    else:
        return False


def get_user_data(user_id: int, table: str):
    if is_user_in_table(user_id, table):
        sql_query = (
            f'SELECT * '
            f'FROM {table} '
            f'WHERE user_id = {user_id}'
        )
        row = execute_query(sql_query)[0]

        return row


def delete_user(user_id: int, table: str):
    if is_user_in_table(user_id, table):
        sql_query = (f'DELETE '
                     f'FROM {table} '
                     f'WHERE user_id = ?')
        execute_query(sql_query, (user_id,))


def create_channels_table():
    sql_query = ('''CREATE TABLE IF NOT EXISTS channels (
                            url TEXT PRIMARY KEY,
                            channel_name TEXT
                       );''')

    execute_query(sql_query)

    for channel in channels.items():
        execute_query('''INSERT OR IGNORE INTO channels (url, channel_name)
                        VALUES (?, ?)''', (channel[1], channel[0]))


def create_users_sb_table():
    execute_query('''CREATE TABLE IF NOT EXISTS users_subscribe_data (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            channel_name TEXT,
                            url TEXT,
                            is_member INTEGER
                       );''')


def create_users_questions_data():
    execute_query('''CREATE TABLE IF NOT EXISTS users_questions_data (
                                id INTEGER PRIMARY KEY,
                                user_id INTEGER,
                                subject TEXT,
                                difficulty TEXT,
                                question TEXT,
                                answer TEXT
                           );''')


def get_table_data(table):
    sql_query = (
        f'SELECT * '
        f'FROM {table};'
    )
    res = execute_query(sql_query)
    return res


def drop(table):
    execute_query(f'DROP TABLE {table};')


create_users_sb_table()
create_channels_table()
