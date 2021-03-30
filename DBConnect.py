"""
Helper class for DB connections
Connects with SQLite DB
"""

import sqlite3
from sqlite3 import Error
from random import random

DATABASE = r"sqlite.db"

# create a connection to the DB
def connect():
    conn = None
    try:
        # connect to sqlite.db
        conn = sqlite3.connect(DATABASE)
        return conn
    except Error as e:
        # print any errors
        print("CONNECT ERROR: ", e)
        exit(0)

"""
create a new table in the db
name: string name of the table
cols: list of strings, data for each column
      eg. ["id integer PRIMARY KEY", "name text NOT NULL"]
      
"""
def create_table(name, cols):
    # create query from input
    sql_query = "CREATE TABLE IF NOT EXISTS " + name + "("
    for i in range(0, len(cols)):
        if(i == 0):
            sql_query += cols[i]
        else:
            sql_query += ", " + cols[i]
    sql_query += ");"

    conn = None
    try:
        # get a db connection
        conn = connect()
        # create a cursor
        cur = conn.cursor()
        # execute statement
        cur.execute(sql_query)
    except Error as e:
        print("CREATE ERROR: ", e)
        exit(0)
    finally:
        if conn:
            conn.close()

"""
select a specific user from the db
username: string username of user to select

return: all rows selected 
"""
def users_select(username):
    sql_query = "SELECT * FROM users WHERE username=?"
    rows = None
    conn = None
    try:
        # get a db connection
        conn = connect()
        # create a cursor
        cur = conn.cursor()
        # execute statement
        cur.execute(sql_query, (username,))
        rows = cur.fetchall()
    except Error as e:
        print("SELECT ALL ERROR: ", e)
        exit(0)
    finally:
        # make sure the connection is closed
        if conn:
            conn.close()
    return rows

"""
select all users from the DB

return: all rows found
"""
def users_select_all():
    sql_query = "SELECT * FROM users"
    rows = None
    conn = None
    try:
        # get a db connection
        conn = connect()
        # create a cursor
        cur = conn.cursor()
        # execute statement
        cur.execute(sql_query)
        rows = cur.fetchall()

    except Error as e:
        print("SELECT ERROR: ", e)
        exit(0)
    finally:
        if conn:
            conn.close()
    return rows

"""
insert one user into the DB
user: data to insert
      eg. (1, "name")
"""
def users_insert(user):
    sql_query = "INSERT INTO users(id, username, password) VALUES(?, ?, ?)"
    conn = None
    try:
        # get a db connection
        conn = connect()
        # create a cursor
        cur = conn.cursor()
        # execute statement
        cur.execute(sql_query, user)

        conn.commit()
    except Error as e:
        print("INSERT ERROR: ", e)
        exit(0)
    finally:
        if conn:
            conn.close()

"""
delete user from the db
id: id of the user to delete 
"""
def users_delete(id):
    sql_query = "DELETE FROM users WHERE id=?"
    conn = None
    try:
        # get a db connection
        conn = connect()
        # create a cursor
        cur = conn.cursor()
        # execute statement
        cur.execute(sql_query, (id,))

        conn.commit()
    except Error as e:
        print("DELETE ERROR: ", e)
        exit(0)
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    users_select_all()
