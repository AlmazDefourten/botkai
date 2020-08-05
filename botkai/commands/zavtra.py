from .. import classes as command_class
import vk_api
import random
import datetime
import json
import requests
from ..keyboards import GetButtonTask
from ..classes import vk, cursor, connection
from ..classes import MessageSettings
from ..classes import UserParams
import traceback

today = datetime.date.today()
chetn = UserParams.getChetn()
BASE_URL = 'https://kai.ru/raspisanie' 
frazi = ["Можно сходить в кино 😚", "Можно почитать 😚", "Можно прогуляться в лесу 😚", "Можно распланировать дела на неделю 😚", "Можно заняться спортом, например. 😚", "Можно вспомнить строчки гимна КАИ 😚", "Можно заняться чем то интересным 😚", "Можно встретиться с друзьями 😚"]
def info():
    today = datetime.date.today()
    date = str(datetime.date(today.year, today.month, today.day)  + datetime.timedelta(days=1))
    group = UserParams.getGroup()
    id = MessageSettings.getId()
    taskCount = (int)(MessageSettings.GetTaskCount(date, UserParams.groupId))
    task = ""
    if taskCount == 0:
        task = "\n&#9993;Заданий нет"
    else:
        task = "\n&#9993;Всего " + str(taskCount) + " задания(-ий)."
    advert = MessageSettings.GetAdv(date, UserParams.groupId)
    adv = ""
    if advert:
        adv = "\n❗ [Объявление] " + MessageSettings.GetAdv(date, UserParams.groupId) + "\n"
    try:
        Timetable =  showTimetable(group, 1)
        if Timetable:
            vk.method("messages.send",
                        {"peer_id": id, "message": "Расписание на завтра:\n" + Timetable + adv +  task, "keyboard": GetButtonTask(date), "random_id": random.randint(1, 2147483647)})
        else:
            vk.method("messages.send",
                        {"peer_id": id, "message": "Завтра занятий нет 😎\n" + frazi[random.randint(0, len(frazi)-1)], "random_id": random.randint(1, 2147483647)})
                        
    except Exception as E:
        print('Ошибка:\n', traceback.format_exc())
        vk.method("messages.send",
                    {"peer_id": id, "message": "Завтра можно отдохнуть :]", "keyboard": GetButtonTask(date), "random_id": random.randint(1, 2147483647)})

    return "ok"

def showTimetable(groupId, tomorrow=0):
    try:
        isNormal, response = getResponse(groupId)
        if not isNormal:
            return response
        chetn = UserParams.getChetn()
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
            print(dateinstr)
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
    
    sql = "SELECT * FROM saved_timetable WHERE groupp = {}".format(groupId)
    cursor.execute(sql)
    result = cursor.fetchone()
    if result == None:
        try:
            
            response = requests.post( BASE_URL, data = "groupId=" + str(groupId), headers = {'Content-Type': "application/x-www-form-urlencoded"}, params = {"p_p_id":"pubStudentSchedule_WAR_publicStudentSchedule10","p_p_lifecycle":"2","p_p_resource_id":"schedule"}, timeout = 3)
        except ConnectionError as err:
            return False, "&#9888;Ошибка подключения к серверу типа ConnectionError. Вероятно, сервера КАИ были выведены из строя.&#9888;"
        except requests.exceptions.Timeout as err:
            return False, "&#9888;Ошибка подключения к серверу типа Timeout. Вероятно, сервера КАИ перегружены.&#9888;"
        except:
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
                response = requests.post( BASE_URL, data = "groupId=" + str(groupId), headers = {'Content-Type': "application/x-www-form-urlencoded"}, params = {"p_p_id":"pubStudentSchedule_WAR_publicStudentSchedule10","p_p_lifecycle":"2","p_p_resource_id":"schedule"}, timeout = 3)
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

command = command_class.Command()

command.keys = ['на завтра', 'расписание на завтра', 'завтра']
command.desciption = 'Расписание на завтра (с учетом четности)'
command.process = info
command.payload = "tomorrow"
command.role = [1,3]