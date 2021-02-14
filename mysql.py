# encoding = utf-8
# =====================================================

#   filename : mysql.py
#   version  : 1.0
#   author   : gongzi xu / 951683309@qq.com
#   date     : 2021/01/29 21:00
#   desc     : 用于对书籍数据库进行操作
# =====================================================
import random
import sqlite3

# import configparser

# # 读取config
# conf = configparser.ConfigParser()
# conf.read('config.ini', encoding="utf-8-sig")
# items = conf.get("DETAIL", "columns").split('，')
import time




def init_database():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()



    c.execute('''create table books_tb(
           _id integer primary key autoincrement,
           book_name text,
           author text,
           book_size double,
           book_format text,

           update_time text,
           tags text

           )''')

    conn.commit()
    c.close()
    conn.close()


def table_exist(table_name):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("select count(*)  from sqlite_master where type='table' and name = '" + table_name + "';")
    result = c.fetchall()
    conn.commit()
    c.close()
    conn.close()

    if result[0][0] == 1:
        return True
    else:
        return False


def insert(table, *arg):
    """
    向表中插入数据
    :param table:
    :param arg:
    :return:
    """
    pass


def add_person(name, phone, card, balance, type):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('insert into user_tb values(null, ?, ?, ?, ?, ?)',
              (name, phone, card, balance, type))
    conn.commit()

    c.close()
    conn.close()


def del_person(id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('select * from user_tb where _id = ' + id)
    result = c.fetchall()
    if result:
        print(result[0][0])
        c.execute('delete from user_tb where _id = ' + str(result[0][0]))
        conn.commit()
    c.close()
    conn.close()


def query(table, key, value):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('select * from ' + table + ' where +' + key + ' = ' + value)
    result = c.fetchall()
    c.close()
    conn.close()
    if result:
        return result
    return None


def query_str(table, key, value):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('select * from ' + table + ' where +' + key + ' = "' + value + '"')
    result = c.fetchall()
    c.close()
    conn.close()
    if result:
        return result
    return None


def like(table, key, value):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('select * from ' + table + ' where +' + key + ' like "%' + value + '%"')
    result = c.fetchall()
    c.close()
    conn.close()

    return result


def max(table):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('SELECT MAX(card) FROM ' + table)
    result = c.fetchall()
    c.close()
    conn.close()

    return result


def update(id, key, value):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('update user_tb set ' + key + ' = "' + value + '" where _id = ' + id)
    conn.commit()
    c.close()
    conn.close()


def add_bill(time, type, cost, balance, name, phone, card, id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('insert into bill_tb values(null, ?, ?, ?, ?, ?, ?, ?, ?)',
              (time, type, cost, balance, name, phone, card, id))
    conn.commit()
    c.close()
    conn.close()


def update_bill(id, key, value):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('update bill_tb set ' + key + ' = "' + value + '" where id = ' + id)
    conn.commit()
    c.close()
    conn.close()


def change_balance(time, balance):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('update balance_tb set balance =?,time =? where _id = 1', (balance, time))
    conn.commit()
    c.close()
    conn.close()


def check_table():
    """
    判断table的完整性
    :return:
    """
    if not table_exist('user_tb'):
        return False
    elif not table_exist('balance_tb'):
        return False
    elif not table_exist('bill_tb'):
        return False
    elif not table_exist('system_tb'):
        return False
    return True




#
# a = range(13000000000, 17800000000)
# b = random.sample(a, 50)
#
# init_database()
#
# def person_in(cost, name, phone, card, balance, id):
#     # balance = float(mysql.query('balance_tb', '_id', '1')[0][2])
#     # balance -= float(cost)
#     add_bill(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
#                    '建户', '+' + str(cost), str(balance), str(name), str(phone), str(card), id)
#
# for i in tqdm(range(50)):
#     j = random.randint(0, 2)
#     if j != 0:
#         x = random.randint(0, len(a1) - 1)
#         y = random.randint(0, len(a2) - 1)
#         z = random.randint(0, len(a2) - 1)
#         name = a1[x] + a2[y] + a2[z]
#     else:
#         x = random.randint(0, len(a1) - 1)
#         y = random.randint(0, len(a2) - 1)
#         name = a1[x] + a2[y]
#
#     add_person(name, b[i], str(i), '0', '')
#     person_in('0', name, b[i], str(i), '0', str(i + 1))
