from __future__ import unicode_literals
from django.http import HttpResponse
# Импортируем модули для работы с JSON и логами.
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from pprint import pprint

sessionStorage = {}
commands = ['расписание']

logging.basicConfig(level=logging.DEBUG)

@csrf_exempt
def main(request):
# Функция получает тело запроса и возвращает ответ.
    body = json.loads(request.body)
    pprint(body)

    response = {
        "version": body['version'],
        "session": body['session'],
        "response": {
            "end_session": False
        }
    }
    return HttpResponse( json.dumps({
  "response": {
    "text": "Здравствуйте! Это мы, хороводоведы.",
    "tts": "Здравствуйте! Это мы, хоров+одо в+еды.",
    
    "end_session": False
  },
  "version": "1.0"
}))


def handle_dialog(body, response):
    request = body["meta"]["request"]
    tokens = request["nlu"]["tokens"]
    entites = request["nlu"]["entites"]
    group_values = ""
    for command in commands:
        if command.lower() in tokens:
            print("Command ", command.lower())
            command = command.lower()
            if command == 'расписание':
                for entity in entites:
                    if entity["type"] == "YANDEX.NUMBER":
                        group_values += entity["value"]
                pritn(group_values)