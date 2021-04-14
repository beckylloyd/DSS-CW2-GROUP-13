"""
Helper class for DB connections
Connects with SQLite DB
"""

import sqlite3
import time
from sqlite3 import Error
from random import random
from datetime import datetime

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
select one row from the DB
sql_query: query to execute
parameters: parameters to include

returns: row found 
"""
def select_one(sql_query, parameters):
    rows = None
    conn = None
    try:
        # get a db connection
        conn = connect()
        # create a cursor
        cur = conn.cursor()
        # execute statement
        cur.execute(sql_query, parameters)
        rows = cur.fetchone()
    except Error as e:
        print("SELECT ERROR: ", e)
        exit(0)
    finally:
        if conn:
            conn.close()
    return rows

"""
select all rows from table 
table: table to select from

return: rows found 
"""
def select_all(table):
    # ok to not be checked, always called from inside this file
    sql_query = "SELECT * FROM "+table+";"
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
        print("SELECT ALL ERROR: ", e)
        exit(0)
    finally:
        if conn:
            conn.close()
    return rows



"""
get the id of a user in the db
username: string username of user to select

return: id of first row returned 
"""
def users_get_id(username):
    sql_query = "SELECT * FROM users WHERE username=?"
    parameters = (username,)
    row = select_one(sql_query, parameters)
    if(row is not None):
        return row[0]
    return None

"""
Get the username associated with the id
id: id to search for

returns: username  
"""
def users_get_username(id):
    sql_query = "SELECT * FROM users WHERE user_id=?"
    parameters = (id,)
    row = select_one(sql_query, parameters)
    if (row is not None):
        return row[1]
    return None

"""
find the password of a user in the db
username: string username of user to select

return: password of first row returned 
"""
def users_get_password(username):
    sql_query = "SELECT * FROM users WHERE username=?"
    parameters = (username,)
    row = select_one(sql_query, parameters)
    if (row is not None):
        return row[2]
    return None

"""
check if a user is in the db
username: string username of user to select

return: username of first row returned 
"""
def users_search_user(username):
    sql_query = "SELECT * FROM users WHERE username=?"
    parameters = (username,)
    row = select_one(sql_query, parameters)
    if (row is not None):
        return row[1]
    return None

"""
select all users from the DB

return: all rows found
"""
def users_get_all():
    return select_all("users")

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



"""
select all posts in the db

returns: list of all posts 
"""
def posts_get_all():
    return select_all("posts")

"""
insert post into the db
post: post t insert (title, body, tag)
user_id: id of user currently logged in
"""
def posts_insert(post, user_id):
    # find post_id based on last post in db
    all_posts = posts_get_all()
    post_id = all_posts[len(all_posts)-1][0] + 1

    # get current date and time
    date = datetime.now().strftime("%d/%m/%Y")
    time = datetime.now().strftime("%H:%M")

    # get tag id
    tag_id = tags_get_id(post[2])

    # create post with all parameters
    insert_post = (post_id, post[0], post[1], date, time, tag_id, user_id)

    # sql query to execute
    sql_query = "INSERT INTO posts(post_id, title, body, date, time, tag_id, user_id) VALUES(?, ?, ?, ?, ?, ?, ?)"

    conn = None
    try:
        # get a db connection
        conn = connect()
        # create a cursor
        cur = conn.cursor()
        # execute statement
        cur.execute(sql_query, insert_post)

        conn.commit()
    except Error as e:
        print("INSERT ERROR: ", e)
        exit(0)
    finally:
        if conn:
            conn.close()



"""
get the name of a tag from the id

id: the id of the tag to search
returns: name of the tag 
"""
def tags_get_name(id):
    sql_query = "SELECT * FROM tags WHERE tag_id=?"
    row = select_one(sql_query, (id,))
    if row is not None:
        return row[1]
    else:
        return None

"""
get the id of a tag from its name

name: the name of the tag to search
returns: int id of the tag 
"""
def tags_get_id(name):
    sql_query = "SELECT * FROM tags WHERE name=?"
    row = select_one(sql_query, (name,))
    if row is not None:
        return row[0]
    else:
        return None

"""
get just the names of all tags in the db

return: list of names as strings 
"""
def tags_get_all_names():
    tags = select_all("tags")
    names = []
    for tag in tags:
        names.append(tag[1])
    return names



"""
log in to the application
username: username from form
password: password from form

returns: bool (logged in or not)
         message: "Log in successful :)" or "Error logging in :("
"""
def login(username, password):
    user_ok = False
    pass_ok = False

    # parse username and password(?)
    username = parse_text(username)
    password = parse_text(password)

    # search for username
    uname = users_search_user(username)
    if(uname == username):
        user_ok = True

    # search for password (even if username incorrect)
    pword = users_get_password(username)
    if(pword == password):
        pass_ok = True

    # check if both correct
    # make sure error message is generic
    if(user_ok and pass_ok):
        return True, "Log in successful :)"
    else:
        return False, "Error logging in :("


"""
search the db
term: user input from the search bar

returns: posts found matching the term
"""
def search(term):

    sql_query = "SELECT * FROM full_posts WHERE title LIKE ? UNION SELECT * FROM full_posts WHERE body LIKE ? UNION SELECT * FROM full_posts WHERE name LIKE ? UNION SELECT * FROM full_posts WHERE username LIKE ?;"
    parameters = ('%' + term + '%', '%' + term + '%','%' + term + '%','%' + term + '%' )
    rows = None
    conn = None
    try:
        # get a db connection
        conn = connect()
        # create a cursor
        cur = conn.cursor()
        # execute statement
        cur.execute(sql_query, parameters)
        rows = cur.fetchall()
    except Error as e:
        print("SEARCH ERROR: ", e)
        exit(0)
    finally:
        if conn:
            conn.close()
    return rows


# just a temp method
# will be properly written in utilities
def parse_text(text):
    return text


if __name__ == '__main__':
    result = search('billy')

    for each in result:
        print(each)
    # print(users_get_id('katerina'))
    # print(users_get_username(1))
    # print(users_get_password('katerina'))
    # print(users_search_user('katerina'))
    # print(users_get_all())
    #
    # print(posts_get_all())
    # print(tags_get_name(1))
    #
    # print(login("katerina", "password1234"))
    # print(login("katerina", "password"))
    # print(login("jessica", "password1234"))



