# -- coding: utf-8 --
import json
import pymysql


def get_connection():
    file = open('../db_config', 'r')
    host = file.readline()
    pwd = file.readline()
    file.close()
    return pymysql.connect(host=host, port=3306, user='admin', password=pwd, db='eva', charset='utf8')


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
    return json.dumps({'state': 'success'}, ensure_ascii=False)


def delete_all():
    conn = get_connection()

    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "DELETE FORM shortcut WHERE id > 0"
    curs.execute(sql)

    rows = curs.fetchall()
    conn.close()

    return json.dumps(rows, default=shortcut_handler,ensure_ascii=False)


def delete_by_user(user_id):
    conn = get_connection()

    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "DELETE FORM shortcut WHERE user_id = %s"
    curs.execute(sql, int(user_id))

    rows = curs.fetchall()
    conn.close()

    return json.dumps({'state': 'success'}, ensure_ascii=False)


def delete_by_keyword(user_id, keyword):
    conn = get_connection()
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "DELETE FORM shortcut WHERE user_id = %s, keyword = %s"
    param = (int(user_id), keyword)
    curs.execute(sql, param)

    rows = curs.fetchall()
    conn.close()

    return json.dumps({'state': 'success'}, ensure_ascii=False)


def find_all():
    conn = get_connection()

    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM shortcut"
    curs.execute(sql)

    rows = curs.fetchall()
    conn.close()

    return json.dumps(rows, default=shortcut_handler,ensure_ascii=False)


def find_by_user(user_id):
    conn = get_connection()

    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM shortcut WHERE user_id = %s"
    curs.execute(sql, int(user_id))

    rows = curs.fetchall()
    conn.close()

    return json.dumps(rows, default=shortcut_handler, ensure_ascii=False)


def find_by_keyword(user_id, keyword):
    conn = get_connection()
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM shortcut WHERE user_id = %s and keyword = %s"
    param = (int(user_id), keyword)
    curs.execute(sql, param)

    rows = curs.fetchall()
    conn.close()

    return json.dumps(rows, default=shortcut_handler, ensure_ascii=False)
