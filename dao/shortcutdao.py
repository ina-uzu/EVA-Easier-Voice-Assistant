# -- coding: utf-8 --
import json
import pymysql


def get_connection():
    return pymysql.connect(host='eva.c09iaudkjatg.ap-northeast-2.rds.amazonaws.com', port=3306, user='admin',
                           password='evaeva2019', db='eva', charset='utf8')


def shortcut_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


def add(user_id, keyword, command):
    conn = get_connection()
    curs = conn.cursor()
    ok = curs.execute("INSERT INTO shortcut(user_id, keyword, command, create_datetime) VALUES (%d,%s,%s, now())",
                      user_id, keyword, command)
    conn.commit()
    conn.close()
    return json.dumps({'rows': ok})


def find_by_user(user_id):
    conn = get_connection()

    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM shortcut WHERE user_id is %d" % user_id
    curs.execute(sql)

    rows = curs.fetchall()
    conn.close()

    return json.dumps(rows, default=shortcut_handler)
