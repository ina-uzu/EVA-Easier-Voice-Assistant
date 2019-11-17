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

    sql = "INSERT INTO shortcut(user_id, keyword, command, create_datetime) VALUES (%s,%s,%s, now())"
    param = (int(user_id), keyword, command)

    ok = curs.execute(sql,param)
    conn.commit()
    conn.close()
    return json.dumps({'rows': ok})


def delete_all(user_id):
    conn = get_connection()

    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "DELETE FORM shortcut WHERE user_id = %s"
    curs.execute(sql, int(user_id))

    rows = curs.fetchall()
    conn.close()

    return json.dumps(rows, default=shortcut_handler)


def delete_by_keyword(user_id, keyword):
    conn = get_connection()
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "DELETE FORM shortcut WHERE user_id = %s, keyword = %s"
    param = (int(user_id), keyword)
    curs.execute(sql, param)

    rows = curs.fetchall()
    conn.close()

    return json.dumps(rows, default=shortcut_handler)


def find_all(user_id):
    conn = get_connection()

    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM shortcut WHERE user_id = %s"
    curs.execute(sql, int(user_id))

    rows = curs.fetchall()
    conn.close()

    return json.dumps(rows, default=shortcut_handler)


def find_by_keyword(user_id, keyword):
    conn = get_connection()
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM shortcut WHERE user_id = %s and keyword = %s"
    param = (int(user_id), keyword)
    curs.execute(sql, param)

    rows = curs.fetchall()
    conn.close()

    return json.dumps(rows, default=shortcut_handler)
