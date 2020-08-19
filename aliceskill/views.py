from __future__ import unicode_literals
from django.http import HttpResponse
# Импортируем модули для работы с JSON и логами.
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from pprint import pprint
import os
import psycopg2
import sqlite3

import random
import datetime
import json
import requests
import traceback


sessionStorage = {}
commands = ['расписание', "что ты умеешь", "помощь"]



class connections:
    def __init__(self):
        self.connection = psycopg2.connect(dbname=os.getenv('DB_NAME'), user= os.getenv('DB_USER'), password= os.getenv('DB_PASSWORD'), host= os.getenv('DB_HOST'))
        self.connection.autocommit=True
        self.cursor = self.connection.cursor()
        self.conn = sqlite3.connect("bot.db")
        self.cursorR = self.conn.cursor()

connect = connections()
cursor = connect.cursor
cursorR = connect.cursorR
connection = connect.connection
conn = connect.conn
today = datetime.date.today()
chetn = 1
BASE_URL = 'https://kai.ru/raspisanie' 
def getGroupsResponse(groupNumber):
    cursor.execute("SELECT shedule FROM saved_timetable WHERE groupp = 1")
    result = cursor.fetchone()[0]
    result = json.loads(result)
    for elem in result:
        if int(elem["group"]) == int(groupNumber):
            return elem["id"]
    return False



def showGroupId(groupNumber):
    try:
        response = requests.post( BASE_URL + "?p_p_id=pubStudentSchedule_WAR_publicStudentSchedule10&p_p_lifecycle=2&p_p_resource_id=getGroupsURL&query=" + groupNumber, headers = {'Content-Type': "application/x-www-form-urlencoded"}, params = {"p_p_id":"pubStudentSchedule_WAR_publicStudentSchedule10","p_p_lifecycle":"2","p_p_resource_id":"schedule"}, timeout = 2)
        if str(response.status_code) != '200':
            raise ConnectionError
            # vk.method("messages.send",
            #     {"peer_id": id, "message": "&#9888;Ошибка подключения к серверам.&#9888; \n Вероятно, на стороне kai.ru произошел сбой. Вам необходимо продолжить регистрацию как только сайт kai.ru станет доступным.", "random_id": random.randint(1, 2147483647)})
            # vk.method("messages.send",
            #         {"peer_id": id, "message": "test" , "sticker_id" : 18486 , "random_id": random.randint(1, 2147483647)})
            
            return False
        print(response.json())
        response = response.json()[0]
        return response['id']
    except IndexError:
        print('Ошибка:\n', traceback.format_exc())
        return False
    except (ConnectionError, TimeoutError, requests.exceptions.ReadTimeout):
        group = getGroupsResponse(groupNumber)
        if group:
            return group
        print('Ошибка:\n', traceback.format_exc())
        return False
    except:
        print('Ошибка:\n', traceback.format_exc())
        return False

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

    handle_dialog(body,request, response)

    return HttpResponse( json.dumps( response))


def handle_dialog(body, request, response):
    session = body["session"]
    new = session["new"]
    request = body["request"]
    original_utterance = request["original_utterance"]
    tokens = request["nlu"]["tokens"]
    entities = request["nlu"]["entities"]
    user_id = session['user_id']
    group_values = ""
    if new:
        sessionStorage[user_id] = {
                    "groupId" : None
                }

        response["response"]["text"] = "Привет! Я смогу тебе подсказать твое расписание - просто попроси меня об этом и обозначь свою группу"
        return
    else:
        try:
            if sessionStorage[user_id]["groupId"]:
                group_values = sessionStorage[user_id]["groupId"]
        except KeyError:
            sessionStorage[user_id] = {
                    "groupId" : None
                }
            

    pre_group_values = ""
    day = ""
    for command in commands:
        if command.lower() in tokens:
            print("Command ", command.lower())
            command = command.lower()
            if command == 'расписание':
                for entity in entities:

                    if entity["type"] == "YANDEX.NUMBER" and len(pre_group_values) < 4:
                        pre_group_values += str(entity["value"])
                    elif entity["type"] == "YANDEX.DATETIME":
                        if "day" in entity["value"]:
                            day = entity["value"]["day"]
                        elif "month" in entity["value"]:
                            day = entity["value"]["month"]

                print(group_values, pre_group_values)
                if pre_group_values != "" and pre_group_values.isdigit() and len(pre_group_values) == 4:
                    group_values = pre_group_values

                if not group_values or group_values == "":
                    response["response"]["text"] = "Повтори все тоже самое, но с номером группы"
                    return
                sessionStorage[user_id] = {
                    "groupId" : group_values
                }
                #response["response"]["text"] = command + " " + group_values + " день " + str(day)
                response["response"]["text"] = info(group_values, day)

            return
        elif original_utterance == 'что ты умеешь' or original_utterance == "помощь":
            response["response"]["text"] = "Я могу тебе подсказать твое расписание - просто попроси меня об этом и обозначь свою группу."
            return


            
        else:
            if new:
                response["response"]["text"] = "Привет! Я смогу тебе подсказать твое расписание - просто попроси меня об этом и обозначь свою группу"
                return
            response["response"]["text"] = "Я не распознал твою команду. Повтори, пожалуйста, что ты хочешь получить и номер группы."



frazi = ["Можно сходить в кино 😚", "Можно почитать 😚", "Можно прогуляться в лесу 😚", "Можно распланировать дела на неделю 😚", "Можно заняться спортом, например. 😚", "Можно вспомнить строчки гимна КАИ 😚", "Можно заняться чем то интересным 😚", "Можно встретиться с друзьями 😚"]
def info(group, day):
    try:
        today = datetime.date.today()
        day = int(day) if (str(day)).isdigit() else 0
        date = str(datetime.date(today.year, today.month, today.day)  + datetime.timedelta(days=1))
        return showTimetable(group, day)
    except:
        print('Ошибка:\n', traceback.format_exc())



def showTimetable(groupId, tomorrow=0):
    try:
        groupId = showGroupId(groupId)
        if not groupId:
            return "Группы не существует"
        isNormal, response = getResponse(groupId)
        if not isNormal:
            print("NOOOOOOOOOOOO")
            return response
        
        today = datetime.date.today() + datetime.timedelta(days=tomorrow)


        if len(response) == 0:
            return "\n&#10060;\tРасписание еще не доступно.&#10060;"
        
        response = response[str(datetime.date(today.year, today.month, today.day).isoweekday())]
        result = ''
        now = datetime.datetime.now() + datetime.timedelta(days=tomorrow)
        month = now.month
        if month < 10:
            month = "0" + str(month)
        day = str(now.day) + "." + str(month)
        for elem in response:
            dateinstr = (str((elem["dayDate"]).rstrip())).find(day)
            if (elem["dayDate"]).rstrip()=="чет" and ((datetime.date(today.year, today.month, today.day).isocalendar()[1] + chetn) % 2 == 0):
                result += str(chr(10148)) + elem["dayDate"][:3] + " " + " &#8987;" + elem["dayTime"][:5] +  " " + elem["disciplType"][:4] + " " + elem["disciplName"] + " " + (elem["audNum"]).rstrip() + " " + (elem["buildNum"]).rstrip() +' зд.\n'
            elif (elem["dayDate"]).rstrip()=="неч" and  not ((datetime.date(today.year, today.month, today.day).isocalendar()[1] + chetn) % 2 == 0):
                result += str(chr(10148)) + elem["dayDate"][:3] + " " + " &#8987;" + elem["dayTime"][:5] + " " + elem["disciplType"][:4] + " " + elem["disciplName"] + " " + (elem["audNum"]).rstrip() + " " + (elem["buildNum"]).rstrip() +' зд.\n'
            elif (elem["dayDate"]).rstrip()=="неч/чет" and  not ((datetime.date(today.year, today.month, today.day).isocalendar()[1] + chetn) % 2 == 0):
                result += str(chr(10148))  + " 1&#8419;гр. " + " &#8987;" + elem["dayTime"][:5] + " " + elem["disciplType"][:4] + " " + elem["disciplName"] + " " + (elem["audNum"]).rstrip() + " " + (elem["buildNum"]).rstrip() +' зд.\n'
            elif (elem["dayDate"]).rstrip()=="неч/чет" and  ((datetime.date(today.year, today.month, today.day).isocalendar()[1] + chetn) % 2 == 0):
                result += str(chr(10148))  + " 2&#8419;гр. " + " &#8987;" + elem["dayTime"][:5] + " " + elem["disciplType"][:4] + " " + elem["disciplName"] + " " + (elem["audNum"]).rstrip() + " " + (elem["buildNum"]).rstrip() +' зд.\n'
            elif (elem["dayDate"]).rstrip()=="чет/неч" and  ((datetime.date(today.year, today.month, today.day).isocalendar()[1] + chetn) % 2 == 0):
                result += str(chr(10148))  + " 1&#8419;гр. " + " &#8987;" + elem["dayTime"][:5] + " " + elem["disciplType"][:4] + " " + elem["disciplName"] + " " + (elem["audNum"]).rstrip() + " " + (elem["buildNum"]).rstrip() +' зд.\n'
            elif (elem["dayDate"]).rstrip()=="чет/неч" and  not ((datetime.date(today.year, today.month, today.day).isocalendar()[1] + chetn) % 2 == 0):
                result += str(chr(10148))  + " 2&#8419;гр. " + " &#8987;" + elem["dayTime"][:5] + " " + elem["disciplType"][:4] + " " + elem["disciplName"] + " " + (elem["audNum"]).rstrip() + " " + (elem["buildNum"]).rstrip() +' зд.\n'
            elif dateinstr != -1:
                result += str(chr(10148)) + str(day) + " " + " &#8987;" + elem["dayTime"][:5] + " " + elem["disciplType"][:4] + " " + elem["disciplName"] + " " + (elem["audNum"]).rstrip() + " " + (elem["buildNum"]).rstrip() + ' зд.\n'
            elif not ((elem["dayDate"]).rstrip()=="чет") and not ((elem["dayDate"]).rstrip()=="неч"):
                result += str(chr(10148)) + elem["dayDate"].rstrip() + " " + " &#8987;" + elem["dayTime"][:5] + " " + elem["disciplType"][:4] + " " + elem["disciplName"] + " " + (elem["audNum"]).rstrip() + " " + (elem["buildNum"]).rstrip() + ' зд.\n'
        return result
    except ConnectionError as err:
        return "&#9888;Ошибка подключения к серверу типа ConnectionError. Вероятно, сервера КАИ были выведены из строя.&#9888;"
    except requests.exceptions.Timeout as err:
        return "&#9888;Ошибка подключения к серверу типа Timeout. Вероятно, сервера КАИ перегружены.&#9888;"
    except KeyError as err:
        return False
    except Exception as E:
        print('Ошибка:\n', traceback.format_exc())

        return ""
    


def getResponse(groupId):
    try:
        sql = "SELECT * FROM saved_timetable WHERE groupp = {}".format(groupId)
        cursor.execute(sql)
        result = cursor.fetchone()
        if result == None:
            try:
                
                response = requests.post( BASE_URL, data = "groupId=" + str(groupId), headers = {'Content-Type': "application/x-www-form-urlencoded"}, params = {"p_p_id":"pubStudentSchedule_WAR_publicStudentSchedule10","p_p_lifecycle":"2","p_p_resource_id":"schedule"}, timeout = 1)
            except ConnectionError as err:
                return False, "&#9888;Ошибка подключения к серверу типа ConnectionError. Вероятно, сервера КАИ были выведены из строя.&#9888;"
            except requests.exceptions.Timeout as err:
                return False, "&#9888;Ошибка подключения к серверу типа Timeout. Вероятно, сервера КАИ перегружены.&#9888;"
            except:
                print('Ошибка:\n', traceback.format_exc())

                return False, ""
            sql = "INSERT INTO saved_timetable VALUES ({}, '{}', '{}')".format(groupId, datetime.date.today(), json.dumps(response.json()))
            cursor.execute(sql)
            connection.commit()
            return True, response.json()
        else:
            date_update = result[1]
            timetable = result[2]
            if date_update + datetime.timedelta(days=4) >= today:
                try:
                    response = requests.post( BASE_URL, data = "groupId=" + str(groupId), headers = {'Content-Type': "application/x-www-form-urlencoded"}, params = {"p_p_id":"pubStudentSchedule_WAR_publicStudentSchedule10","p_p_lifecycle":"2","p_p_resource_id":"schedule"}, timeout = 1)
                    sql = "UPDATE saved_timetable SET shedule = '{}', date_update = '{}' WHERE groupp = {}".format(json.dumps(response.json()), datetime.date.today(), groupId)
                    cursor.execute(sql)
                    connection.commit()
                    return True, response.json()
                except:
                    sql = "SELECT shedule FROM saved_timetable WHERE groupp = {}".format(groupId)
                    cursor.execute(sql)
                    result = cursor.fetchone()[0]
                    return True, json.loads(result)
            else:
                sql = "SELECT shedule FROM saved_timetable WHERE groupp = {}".format(groupId)
                cursor.execute(sql)
                result = cursor.fetchone()[0]
                return True, json.loads(result)
        
        


        return 
    except:
        print('Ошибка:\n', traceback.format_exc())
