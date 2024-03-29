import requests
from log import logger
from transformers import AutoTokenizer
from data import get_user_data
from config import HEADERS, URL


class GPT:
    def __init__(self, system_content=''):
        self.system_content = system_content
        self.URL = 'http://localhost:1234/v1/chat/completions'
        self.HEADERS = {"Content-Type": "application/json"}
        self.MAX_TOKENS = 50
        self.assistant_content = "решим задачу по шагам: "

    # Подсчитываем количество токенов в промте
    @staticmethod
    def count_tokens(prompt) -> int:
        tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")  # название модели
        return len(tokenizer.encode(prompt))

    # Проверка ответа на возможные ошибки и его обработка
    def process_resp(self, response) -> [bool, str]:
        # Проверка статус кода
        if response.status_code < 200 or response.status_code >= 300:
            self.clear_history()
            error_msg = f"Ошибка: {response.status_code}"
            logger.error(error_msg)
            return False, error_msg

        # Проверка json
        try:
            full_response = response.json()
        except:
            self.clear_history()
            return False, "Ошибка получения JSON"

        # Проверка сообщения об ошибке
        if "error" in full_response or 'choices' not in full_response:
            self.clear_history()
            return False, f"Ошибка: {full_response}"

        # Результат
        result = full_response['choices'][0]['message']['content']

        # Сохраняем сообщение в историю
        self.save_history(result)

        # Пустой результат == объяснение закончено
        if not result:
            return True, 'объяснение закончено'
        else:
            return True, result

    # Формирование промта
    def make_promt(self, user_request) -> dict:
        json = {
            "messages": [
                {
                    "role": "system",
                    "content": self.system_content
                },
                {
                    "role": "user",
                    "content": user_request
                },
                {
                    "role": "assistant",
                    "content": self.assistant_content
                },
            ],
            "temperature": 1.2,
            "max_tokens": self.MAX_TOKENS,
        }
        return json

    # Отправка запроса
    def send_request(self, json):
        resp = requests.post(url=self.URL, headers=self.HEADERS, json=json)
        return resp

    # Сохраняем историю общения
    def save_history(self, content_response) -> None:
        # Твой код ниже
        self.assistant_content += content_response + '\n'

    # Очистка истории общения
    def clear_history(self) -> None:
        # Твой код ниже
        self.assistant_content = "история предыдущих сообщений: "


def make_system_promt(user_id) -> str:
    user = get_user_data(user_id, 'users_questions_data')[0]
    diff = user[3]
    sub = user[2]
    promt = f'ты помощник по предмету {sub}, ты должен ответить на вопрос собеседника, учитывая что его уровень знаний - {diff}. Отвечай на русском'
    return promt


def gpt_dialog(user_request, user_id):
    text = make_system_promt(user_id)
    gpt = GPT(system_content=text)
    # Проверка запроса на количество токенов
    request_tokens = gpt.count_tokens(user_request)
    if request_tokens > gpt.MAX_TOKENS:
        return "Запрос несоответствует кол-ву токенов"

    # НЕ продолжаем ответ и начинаем общаться заново
    if user_request.lower() != 'продолжи':
        gpt.clear_history()

    # Формирование промта
    json = gpt.make_promt(user_request)

    # Отправка запроса
    resp = gpt.send_request(json)

    # Проверяем ответ на наличие ошибок и парсим его
    response = gpt.process_resp(resp)
    if not response[0]:
        return "Не удалось выполнить запрос..."
        # Выводим ответ или сообщение об ошибке
    return response[1]
