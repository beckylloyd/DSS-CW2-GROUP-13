"""
Helper class for DB connections
Connects with SQLite DB
"""

import sqlite3

import time
from sqlite3 import Error
from random import random
from datetime import datetime
from email.message import EmailMessage
import smtplib
DATABASE = r"sqlite.db"

"""
only authorises select queries
"""
def select_authoriser(sqltype, arg1, arg2, dbname, source):
    if sqltype == sqlite3.SQLITE_SELECT or sqltype == sqlite3.SQLITE_READ:
        return sqlite3.SQLITE_OK
    else:
        return sqlite3.SQLITE_DENY
"""
only authorises insert queries 
"""
def insert_authoriser(sqltype, arg1, arg2, dbname, source):
    if sqltype == sqlite3.SQLITE_INSERT or sqltype == sqlite3.SQLITE_TRANSACTION:
        return sqlite3.SQLITE_OK
    else:
        return sqlite3.SQLITE_DENY

"""
create a connection to the DB
"""
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
        # set authoriser for select statements
        conn.set_authorizer(select_authoriser)
        # create a cursor
        cur = conn.cursor()
        # execute statement
        cur.execute(sql_query, parameters)
        rows = cur.fetchone()
    except Error as e:
        print("SELECT ERROR: ", e)
        return None
    finally:
        if conn:
            conn.close()
    return rows

"""
select all rows from table 
sql_query: select all statement 

return: rows found 
"""
def select_all(sql_query):
    rows = None
    conn = None
    try:
        # get a db connection
        conn = connect()
        # set authoriser for select statements
        conn.set_authorizer(select_authoriser)
        # create a cursor
        cur = conn.cursor()
        # execute statement
        cur.execute(sql_query)
        rows = cur.fetchall()
    except Error as e:
        print("SELECT ALL ERROR: ", e)
        return None
    finally:
        if conn:
            conn.close()
    return rows



"""
get the id of a user in the db
email: string email of user to select

return: id of first row returned 
"""
def users_get_id(email):
    sql_query = "SELECT * FROM users WHERE email=?"
    parameters = (email,)
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
email: string email of user to select

return: password of first row returned 
"""
def users_get_password(email):
    sql_query = "SELECT * FROM users WHERE email=?"
    parameters = (email,)
    row = select_one(sql_query, parameters)
    if (row is not None):
        return row[2]
    return None

"""
check if a user is in the db
email: string email of user to select

return: email of first row returned 
"""
def users_search_user(email):
    sql_query = "SELECT * FROM users WHERE email=?"
    parameters = (email,)
    row = select_one(sql_query, parameters)
    if (row is not None):
        return row[3]
    return None

"""
get the email of a user in the db
username: string username of user to select

return: email linked to the username provided 
"""
def users_get_email(username):
    sql_query = "SELECT * FROM users WHERE username=?"
    parameters = (username,)
    row = select_one(sql_query, parameters)
    if (row is not None):
        return row[3]
    return None
"""
select all users from the DB

return: all rows found
"""
def users_get_all():
    return select_all("SELECT * FROM users;")

"""
insert one user into the DB
user: data to insert (email, username, password)
"""
def users_insert(user):
    sql_query = "INSERT INTO users(user_id, username, password, email) VALUES(?, ?, ?, ?);"
    all_users = users_get_all()
    id = all_users[len(all_users) -1][0] + 1
    insert_user = (id, user[1], user[2], user[0])
    conn = None
    try:
        # get a db connection
        conn = connect()
        # set authoriser to insert only
        conn.set_authorizer(insert_authoriser)
        # create a cursor
        cur = conn.cursor()
        # execute statement
        cur.execute(sql_query, insert_user)
        conn.commit()
    except Error as e:
        print("INSERT ERROR: ", e)
        return False
    finally:
        if conn:
            conn.close()
    return True

"""
select all posts in the db

returns: list of all posts 
"""
def posts_get_all():
    posts = select_all("SELECT * FROM posts;")
    posts.sort(reverse = True, key=lambda x:datetime.strptime(x[3] + " " + x[4], "%d/%m/%Y %H:%M"))
    return posts

"""
insert post into the db
post: post t insert (title, body, tag)
user_id: id of user currently logged in
"""
def posts_insert(post, user_id):
    # find post_id based on last post in db
    all_posts = select_all("SELECT * FROM posts;")
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
        # set authoriser to only allow inserts
        conn.set_authorizer(insert_authoriser)
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
    names =  select_all("SELECT name FROM tags;")
    ret = []
    for name in names:
        ret.append(name[0])
    return ret


"""
log in to the application
username: username from form
password: password from form

returns: bool (logged in or not)
         message: "Log in successful :)" or "Error logging in :("
"""
def login(email, password):
    user_ok = False
    pass_ok = False

    # parse email and password(?)
    email = parse_text(email)
    password = parse_text(password)

    # search for username
    user = users_search_user(email)
    if(user == email):
        user_ok = True

    # search for password (even if username incorrect)
    pword = users_get_password(email)
    if(pword == password):
        pass_ok = True

    # check if both correct
    # make sure error message is generic
    if(user_ok and pass_ok):
        return True, "Log in successful :)"
    else:
        return False, "Error logging in :("

"""
sign up to the application
email: email from form 
username: username from form
password: password from form

returns: mesage 
"""
def signUp(email, username, password):
    new_user = False
    message = ""
    # parse input text
    email = parse_text(email)
    username = parse_text(username)
    password = parse_text(password)

    # if username exists
        # error on page
    # else send email
        # if email new- say welcome
        # else- say account exists

    # see if username already exists
    result = users_get_email(username)
    if result is not None:
        # username already exists
        message = "This username already exists"
    else:
        # see if the email address is already used
        result = users_search_user(email)
        if result is not None:
            # email already exists
            sendEmail(email, "Hi there "+username+" !\nThis email address has already been used to sign up to Brickin' It :o. Please log in instead!")
        else:
            # new email
            hashedPass = hash(password)
            inserted = users_insert((email, username, hashedPass))
            if inserted:
                new_user = True
                sendEmail(email, "Hi there "+username+" !\nYou have created an account with Brickin' It! :D\n You can now log in!")
            else:
                sendEmail(email, "Hi there "+username+" !\nUnfortunately we couldn't create an account for you :( Please try again later")

        message = "An email has been sent to: " + email +" Please check your inbox for more details!"
    return new_user, message

def sendEmail(address, message):
    sender = 'Brickin\' it! <group08.studyplanner@gmail.com>'

    email = EmailMessage()
    email['From'] = sender
    email['To'] = address
    email['Subject'] = "Brickin' it"
    email.set_content(message)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login("group08.studyplanner@gmail.com", "group08!")
        server.send_message(email)
        server.close()
        print("sent!")
    except smtplib.SMTPException as e:
        print("ERROR: ")
        print(e)

"""
search the db
term: user input from the search bar

returns: posts found matching the term
"""
def search(term):

    sql_query = "SELECT * FROM full_posts WHERE title LIKE ? UNION SELECT * FROM full_posts WHERE body LIKE ? UNION SELECT * FROM full_posts WHERE name LIKE ? UNION SELECT * FROM full_posts WHERE username LIKE ? ORDER BY date;"
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
        rows.sort(reverse=True, key=lambda x: datetime.strptime(x[3] + " " + x[4], "%d/%m/%Y %H:%M"))
    except Error as e:
        print("SEARCH ERROR: ", e)
        exit(0)
    finally:
        if conn:
            conn.close()

    return rows


# just temp methods
# will be properly written in utilities
def parse_text(text):
    return text
def hash(text):
    return text

# if __name__ == '__main__':
#     # print(signUp("katerina.holdsworth@gmail.com", "new", "pass")) # new new
#     # print(signUp("katerina.holdsworth@gmail.com", "new2", "pass")) # old new
#     # print(signUp("katerina.holdsworth@gmail.com", "katerina", "pass")) # new old
#     print(signUp("katerina@email.com", "katerina", "pass")) # old old




