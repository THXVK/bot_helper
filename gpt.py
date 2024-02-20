import requests

URL = 'http://localhost:1234/v1/chat/completions'
HEADERS = {"Content-Type": "application/json"}

MAX_TOKENS = 100


# Формирование промта
def make_promt(user_request):
    json = {
        "messages": [
            {
                "role": "system",
                "content": "Тебя зовут Глебглоб, ты должен отвечать на русском, но заменять все корни слов на бессмысленный набор слогов"
            },
            {
                "role": "user",
                "content": user_request
            },
        ],
        "temperature": 1.2,
        "max_tokens": MAX_TOKENS,
    }
    return json


# Проверка ответа на возможные ошибки и его обработка
def process_resp(response):
    if response.status_code != 200:
        return f'Ошибка запроса, код {response.status_code}'
    json = response.json()
    choice = json['choices'][0]
    return choice['message']['content']


# Отправка и обработка запроса к GPT
def send_request():
    # Получение запроса от пользователя
    user_request = input("Введите запрос к GPT: ")
    responce = requests.post(URL, headers=HEADERS, json=make_promt(user_request))
    message_text = process_resp(responce)
    print(message_text)


def end():
    print("До новых встреч!")
    exit(0)


def start():
    menu = {
        "1": {
            "text": "Запрос к GPT",
            "func": send_request
        },
        "2": {
            "text": "Выход",
            "func": end
        }
    }

    print("Добро пожаловать в Чат-с-GPT")
    # Бесконечный цикл
    while True:
        # Вывод меню
        print("Меню:")
        for num, item in menu.items():
            print(f"{num}. {item['text']}")

        # Получение корректного выбора пользователя
        choice = input("Выберите: ")
        while choice not in menu:
            choice = input("Выберите корректный пункт: ")

        # Вызов функции из меню
        menu[choice]['func']()


if __name__ == "__main__":
    start()
