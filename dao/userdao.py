# -- coding: utf-8 --
#처리된 데이터를 json형식으로 리턴해주기위해 사용
import json
#python mysql 연결 드라이버
import pymysql

def getConnection():
    return pymysql.connect(host='localhost', port=3306, user='root', password='ina@kokoho97',
                           db='eva', charset='utf8')

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
