# -- coding: utf-8 --
import json
import pymysql


def get_connection():
    file = open('db_config', 'r')
    host = file.readline().replace('\n', '')
    pwd = file.readline().replace('\n', '')
    file.close()
    return pymysql.connect(host=host, port=3306, user='admin', password=pwd, db='eva', charset='utf8')


def user_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


def add(name):
    conn = get_connection()
    curs = conn.cursor()
    ok = curs.execute("INSERT INTO user(name, create_datetime) VALUES (%s, now())", name)
    conn.commit()
    conn.close()

    return json.dumps({'state': 'Success'}, ensure_ascii=False)


def delete_by_id(user_id):
    conn = get_connection()
    curs = conn.cursor()
    ok = curs.execute("UPDATE user SET delete_datetime = now() WHERE id = %s", int(user_id))
    conn.commit()
    conn.close()

    return json.dumps({'state': 'Success'}, ensure_ascii=False)


def find_by_id(user_id):
    conn = get_connection()
    curs = conn.cursor()
    curs.execute("SELECT * FROM user WHERE id = %s", int(user_id))
    rows = curs.fetchall()

    print(rows)
    conn.commit()
    conn.close()

    return json.dumps(rows, default=user_handler, ensure_ascii=False)


def find_all():
    conn = get_connection()

    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM user"
    curs.execute(sql)

    rows = curs.fetchall()
    conn.close()

    return json.dumps(rows, default=user_handler, ensure_ascii=False)
