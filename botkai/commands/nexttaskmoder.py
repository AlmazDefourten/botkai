import classes as command_class
import vk_api
import random
import keyboards
from main import vk, cursor, connection
from message_class import MessageSettings
from user_class import UserParams
import datetime
import sqlite3
import psycopg2
import traceback
import datetime

##################################                Добавить блокировку от 3 варнов 
def info():
    id = MessageSettings.getId()
    idAdv = MessageSettings.payload["id"]
    cursor.execute('UPDATE Task SET "IsCheked" = 1 WHERE id = ' + str(idAdv))
    try:
        #sql = "INSERT INTO Status VALUES (" + str(id) + ", 100);"
        #cursorR.execute(sql)
        #conn.commit()
        #conn.close()
        cursor.execute('SELECT * FROM Task WHERE "IsCheked" < 1 LIMIT 1')
        res = cursor.fetchone()
       
        if res:
            ans = "Задание §\n"
            ans += "\nid " + str(res[0]) + " from @id" + str(res[2])
            ans += "\n date: " + str(res[3])
            ans += "\n" + str(res[4])
            vk.method("messages.send",
                {"peer_id": id, "message": str(ans), "keyboard": keyboards.GetModerTaskButton(res[0]), "attachment": str(res[5]), "random_id": random.randint(1, 2147483647)})
        else:
            vk.method("messages.send",
                {"peer_id": id, "message": "Все проверено", "random_id": random.randint(1, 2147483647)})
    except Exception as E:
        print('Ошибка:\n', traceback.format_exc())
        #conn.rollback()
        vk.method("messages.send",
            {"peer_id": id, "message": "Произошла ошибка. Модерация", "random_id": random.randint(1, 2147483647)})
    return "ok"





command = command_class.Command()




command.keys = ['']
command.desciption = ''
command.process = info
command.payload = "nexttask"
