# -- coding: utf-8 --
import json
import pymysql

def getConnection():
    return pymysql.connect(host='eva.c09iaudkjatg.ap-northeast-2.rds.amazonaws.com', port=3306, user='admin', password='evaeva2019',
                           db='eva', charset='utf8')
def user_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

def user_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

def createUser(name):
    conn = getConnection()
    curs = conn.cursor()
    ok = curs.execute("INSERT INTO user(name, create_datetime) VALUES (%s, now())", name)
    conn.commit()
    conn.close()

    return json.dumps({'rows': ok})


def getAllUsers():
    conn = getConnection()

    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM user"
    curs.execute(sql)
   
    rows = curs.fetchall()
    conn.close()

    return json.dumps(rows, default=user_handler)
