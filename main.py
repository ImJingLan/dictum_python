from flask import Flask, redirect, url_for, request, render_template

import json
import sqlite3
from random import randint
import base64


def salt(times):
    rawsalts = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    salts = ''
    for i in range(0, times):
        salts = salts + rawsalts[int(randint(0, 62)) - 1]
    return salts


def dictums():
    con = sqlite3.connect("./datebase.db")
    cur = con.cursor()
    result = cur.execute(
        'SELECT * FROM dic_dictum order by random() limit 1').fetchall()
    id = result[0][0]
    author = result[0][1]
    creator = result[0][2]
    text = result[0][3]
    con.commit()
    cur.close()
    con.close()
    data = [{'id': id, 'author': author, 'creator': creator, 'text': text}]
    data_json = json.dumps(data)
    return data_json


def site_info():
    con = sqlite3.connect("./datebase.db")
    cur = con.cursor()
    result = cur.execute('SELECT * FROM dic_siteinfo').fetchall()
    con.commit()
    cur.close()
    con.close()
    return result[0]


app = Flask(__name__)


@app.route('/')
def index():
    con = sqlite3.connect("./datebase.db")
    cur = con.cursor()

    listOfTables1 = cur.execute(
        """SELECT name FROM sqlite_master WHERE type='table'
  AND name='dic_dictum'; """).fetchall()
    listOfTables2 = cur.execute(
        """SELECT name FROM sqlite_master WHERE type='table'
  AND name='dic_users'; """).fetchall()
    listOfTables3 = cur.execute(
        """SELECT name FROM sqlite_master WHERE type='table'
  AND name='dic_siteinfo'; """).fetchall()
    if listOfTables1 == [] or listOfTables2 == [] or listOfTables3 == []:
        return render_template('install_none.html')
    else:
        sitename = site_info()[1]
    return render_template('index.html', sitename=sitename)


@app.route('/api/', methods=['POST', 'GET'])
def api():
    return dictums()


@app.route('/install/', methods=['POST', 'GET'])
def install():
    con = sqlite3.connect("./datebase.db")
    cur = con.cursor()

    listOfTables1 = cur.execute(
        """SELECT name FROM sqlite_master WHERE type='table'
  AND name='dic_dictum'; """).fetchall()
    listOfTables2 = cur.execute(
        """SELECT name FROM sqlite_master WHERE type='table'
  AND name='dic_users'; """).fetchall()
    listOfTables3 = cur.execute(
        """SELECT name FROM sqlite_master WHERE type='table'
  AND name='dic_siteinfo'; """).fetchall()
    cur.close()
    con.close()
    if request.method == 'POST':
        data = request.form
        con = sqlite3.connect("./datebase.db")
        cur = con.cursor()
        if listOfTables1 == [] and listOfTables2 == [] and listOfTables3 == []:
            sql = '''CREATE TABLE dic_dictum (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author VARCHAR(30) NOT NULL,
            creator VARCHAR(30) NOT NULL,
            text VARCHAR(21775),
            reg_date TIMESTAMP
            );
            '''
            cur.execute(sql)
            con.commit()

            sql = '''CREATE TABLE dic_siteinfo (
            ID INTEGER PRIMARY KEY AUTOINCREMENT, 
            title text NOT NULL,
            describe text NOT NULL,
            keywords text NOT NULL
            )
            '''

            cur.execute(sql)
            con.commit()

            sql = '''CREATE TABLE dic_users (
            ID INTEGER PRIMARY KEY AUTOINCREMENT, 
            username text NOT NULL,
            passwd text NOT NULL,
            email text NOT NULL,
            salt1 text NOT NULL,
            salt2 text NOT NULL,
            usergroup text
            )   
            '''
            cur.execute(sql)
            con.commit()

            sql = """INSERT INTO dic_dictum (creator, author, text)
            VALUES('Dictum Team', 'Dictum Team', 'Welcome To Dictum Python')"""
            cur.execute(sql)
            con.commit()

            sql = """INSERT INTO dic_siteinfo (title, describe, keywords)
            VALUES('""" + data['sitename'] + """', 'Dictum语录站', 'Dictum,语录')"""
            cur.execute(sql)
            con.commit()

            salt1 = salt(10)
            salt2 = salt(10)
            adminpwd = salt1 + data['passwd'] + salt2
            sql = "INSERT INTO dic_users (`username`, `passwd`, `email` , `salt1`, `salt2`, `usergroup`) VALUES ('" + \
                data['username']+"', '"+base64.b64encode(
                    adminpwd.encode()).decode()+"', '"+data['email']+"' ,'"+salt1+"', '"+salt2+"', 'super');"
            cur.execute(sql)
            con.commit()
            cur.close()
            con.close()
            return render_template('install/install_done.html')
        else:
            return render_template('install/install_has_done.html')

    else:
        if listOfTables1 == [] and listOfTables2 == [] and listOfTables3 == []:
            return render_template('install/install.html')
        else:
            return render_template('install/install_has_done.html')


@app.route("/dashboard/")
def dashboard():
    return render_template('dashboard/main.html')


if __name__ == "__main__":
    app.run(port=8586, debug=True)
