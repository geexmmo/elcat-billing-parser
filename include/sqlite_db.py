import sqlite3
import logging

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,datefmt="%H:%M:%S")

def sql_connection(dbfilename):
    try:
        con = sqlite3.connect(dbfilename)
        return con
    
    except IOError as e:
        logging.error("Oops")
        logging.error(e)

def Sqlite_inittable(dbfilename):
    con = sql_connection(dbfilename)
    cursorObj = con.cursor()
    cursorObj.execute("CREATE TABLE accounts(ID INTEGER PRIMARY KEY AUTOINCREMENT, name text, number text, password text)")
    con.commit()
    return

def Sqlite_insert(dbfilename, name, number, password):
    check_if_existing=Sqlite_select_number(dbfilename, number)
    if check_if_existing != None:
        print('Duplicate number submited to database, ignoring: ', number)
        # exit(0)
    else:
        con = sql_connection(dbfilename)
        cursorObj = con.cursor()
        cursorObj.execute('INSERT INTO accounts(name, number, password) VALUES(?, ?, ?)', [name, number, password])
        con.commit()
    return


def Sqlite_remove_number(dbfilename, number):
    con = sql_connection(dbfilename)
    cursorObj = con.cursor()
    cursorObj.execute('DELETE FROM accounts WHERE number = (?)', [number])
    con.commit()

def Sqlite_count(dbfilename):
    con = sql_connection(dbfilename)
    cursorObj = con.cursor()
    cursorObj.execute('SELECT COUNT(*) FROM accounts')
    return cursorObj.fetchone()[0]

def Sqlite_select_number(dbfilename, number):
    con = sql_connection(dbfilename)
    cursorObj = con.cursor()
    cursorObj.execute('SELECT * FROM accounts WHERE number = (?)', [number])
    return cursorObj.fetchone() # fetching only 'number' row

def Sqlite_select_all(dbfilename):
    con = sql_connection(dbfilename)
    cursorObj = con.cursor()
    cursorObj.execute('SELECT * FROM accounts')
    return cursorObj.fetchall()

