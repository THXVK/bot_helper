import requests

URL = 'http://localhost:1234/v1/chat/completions'
HEADERS = {"Content-Type": "application/json"}

MAX_TOKENS = 50
TEXT = "Тебя зовут Глебглоб, ты должен отвечать на русском, но заменять в своем ответе все корни слов на бессмысленный набор слогов. Ты не должен беспокоиться о правильности ответа и пояснять его"


# Формирование промта
def make_promt(user_request):
    json = {
        "messages": [
            {
                "role": "system",
                "content": TEXT
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
def send_request(user_request):
    # Получение запроса от пользователя
    responce = requests.post(URL, headers=HEADERS, json=make_promt(user_request))
    message_text = process_resp(responce)
    return message_text
