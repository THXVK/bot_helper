import json

channels = [
    {'канал 1': 'derteafg'},
    {'канал 2': 'SDFWDGW'},
    {'канал 3': 'sdfsadfsdeq'},
    {'канал 4': 'sertsdfgWS'},
]

settings_1 = {
    'Русский': 'Russian',
    'Математика': 'Math'

}

settings_2 = {

    ...
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
