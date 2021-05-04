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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os
import Utilities
DATABASE = r"sqlite.db"

EMAIL_EXISTS = "You already have an account with this email address! Please log in to continue!"
USER_CREATE = "You have sucessfully made an account! Please log in to continue!"


"""
authorisers check that a query only executes commands that are valid
"""
def select_authoriser(sqltype, arg1, arg2, dbname, source):
    if sqltype == sqlite3.SQLITE_SELECT or sqltype == sqlite3.SQLITE_READ:
        return sqlite3.SQLITE_OK
    else:
        return sqlite3.SQLITE_DENY

def insert_authoriser(sqltype, arg1, arg2, dbname, source):
    if sqltype == sqlite3.SQLITE_INSERT or sqltype == sqlite3.SQLITE_TRANSACTION:
        return sqlite3.SQLITE_OK
    else:
        return sqlite3.SQLITE_DENY

def update_authoriser(sqltype, arg1, arg2, dbname, source):
    if sqltype == sqlite3.SQLITE_READ or sqltype == sqlite3.SQLITE_TRANSACTION or sqltype == sqlite3.SQLITE_UPDATE:
        return sqlite3.SQLITE_OK
    else:
        return sqlite3.SQLITE_DENY

def delete_authoriser(sqltype, arg1, arg2, dbname, source):
    if sqltype == sqlite3.SQLITE_DELETE or sqltype == sqlite3.SQLITE_READ or sqltype == sqlite3.SQLITE_TRANSACTION:
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
select multiple rows from the DB
sql_query: query to execute
parameters: parameters to include

returns: rows found 
"""
def select_all(sql_query, parameters):
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
        rows = cur.fetchall()
    except Error as e:
        print("SELECT ALL ERROR: ", e)
        return None
    finally:
        if conn:
            conn.close()
    return rows

"""
insert data into the db
sql_query: query to execute
parameters: parameters to include

returns: bool is inserted 
"""
def insert(sql_query, parameters):
    try:
        # get a db connection
        conn = connect()
        # set authoriser to insert only
        conn.set_authorizer(insert_authoriser)
        # create a cursor
        cur = conn.cursor()
        # execute statement
        cur.execute(sql_query, parameters)
        conn.commit()
    except Error as e:
        print("INSERT ERROR: ", e)
        return False
    finally:
        if conn:
            conn.close()
    return True

"""
update a row in the db
sql_query: query to execute
parameters: parameters to include

returns: bool is updated 
"""
def update(sql_query, parameters):
    try:
        # get a db connection
        conn = connect()
        # set authoriser to update only
        conn.set_authorizer(update_authoriser)
        # create a cursor
        cur = conn.cursor()
        # execute statement
        cur.execute(sql_query, parameters)
        conn.commit()
    except Error as e:
        print("UPDATE ERROR: ", e)
        return False
    finally:
        if conn:
            conn.close()
    return True

"""
delete data from the db
sql_query: query to execute
parameters: parameters to include

returns: bool is deleted
"""
def delete(sql_query, parameters):
    try:
        # get a db connection
        conn = connect()
        # set authoriser to delete only
        conn.set_authorizer(delete_authoriser)
        # create a cursor
        cur = conn.cursor()
        # execute statement
        cur.execute(sql_query, parameters)
        conn.commit()
    except Error as e:
        print("DELETE ERROR: ", e)
        return False
    finally:
        if conn:
            conn.close()
    return True


# get the id of a user given the email
def users_get_id(email):
    sql_query = "SELECT * FROM users WHERE email=?"
    parameters = (email,)
    row = select_one(sql_query, parameters)
    if(row is not None):
        return row[0]
    return None

# get the id of a user given the username
def users_get_id_u(username):
    sql_query = "SELECT * FROM users WHERE username=?"
    parameters = (username,)
    row = select_one(sql_query, parameters)
    if(row is not None):
        return row[0]
    return None

# get the username of a user given the id
def users_get_username(id):
    sql_query = "SELECT * FROM users WHERE user_id=?"
    parameters = (id,)
    row = select_one(sql_query, parameters)
    if (row is not None):
        return row[2]
    return None

# get the password of a user given the email
def users_get_password(email):
    sql_query = "SELECT * FROM users WHERE email=?"
    parameters = (email,)
    row = select_one(sql_query, parameters)
    if (row is not None):
        return row[3]
    return None

# search for a user given the email
def users_search_user(email):
    sql_query = "SELECT * FROM users WHERE email=?"
    parameters = (email,)
    row = select_one(sql_query, parameters)
    if (row is not None):
        return row[1]
    return None

# get the email of a user given the username
def users_get_email(username):
    sql_query = "SELECT * FROM users WHERE username=?"
    parameters = (username,)
    row = select_one(sql_query, parameters)
    if (row is not None):
        return row[1]
    return None

# get specfic details of a user given the username
def users_get_details(username):
    sql_query = "SELECT username, image, bio FROM users WHERE username=?"
    parameters = (username,)
    return select_one(sql_query, parameters)

# get the date and time a user was added to the db given the email
def users_get_added(email):
    sql_query = "SELECT * FROM users WHERE email=?"
    parameters = (email,)
    row = select_one(sql_query, parameters)
    if (row is not None):
        return row[4]
    return None

# select all users from the db
def users_get_all():
    return select_all("SELECT * FROM users;", ())

# insert a user into the db (email, username, password)
def users_insert(user):
    sql_query = "INSERT INTO users(user_id, email, username, password, added, seasoning) VALUES(?, ?, ?, ?, ?, ?);"
    all_users = users_get_all()
    id = all_users[len(all_users) -1][0] + 1
    added = datetime.now()
    salt = str(os.urandom(16))
    readFile= Utilities.readFile("pepper.txt")
    pepper = Utilities.decrypt(readFile[0], datetime.strptime(readFile[1], "%d/%m/%Y %H:%M:%S:%f"))
    hashed = Utilities.hash(pepper+user[2]+salt, added)

    insert_user = (id, user[0], user[1], hashed, added.strftime("%d/%m/%Y %H:%M:%S:%f"), salt)
    return insert(sql_query, insert_user)

# update the bio of a user given the username
def users_update_bio(username, bio):
    user_id = users_get_id_u(username)
    sql_query = "UPDATE users SET bio=? WHERE user_id=?"
    parameters = (bio, user_id)
    return update(sql_query, parameters)

# update the image of a user given the username
def users_update_image(username, image):
    user_id = users_get_id_u(username)
    sql_query = "UPDATE users SET image=? WHERE user_id=?"
    parameters = (image, user_id)
    return update(sql_query, parameters)

# get the salt associated with a user
def users_get_salt(email):
    sql_query = "SELECT * FROM users WHERE email=?"
    parameters = (email,)
    row = select_one(sql_query, parameters)
    if (row is not None):
        return row[7]
    return None



# get all the posts from the db
def posts_get_all():
    posts = select_all("SELECT * FROM posts;", ())
    posts.sort(reverse = True, key=lambda x:datetime.strptime(x[3] + " " + x[4], "%d/%m/%Y %H:%M"))
    return posts

# get all the posts made by a specific user
def posts_from_user(username):
    user_id = users_get_id_u(username) # [Title, date, time, post text, username, post_id]
    if user_id is not None:
        sql_query = "SELECT title, date, time, body, user_id, post_id from posts where user_id=?"
        parameters = (user_id,)
        posts = select_all(sql_query, parameters)
        all_posts = []
        for post in posts:
            username = users_get_username(post[4])
            title = Utilities.unencode(post[0])
            body = Utilities.unencode(post[3])
            all_posts.append([title, post[1], post[2], body, username, post[5]])
        return all_posts
    return None

# insert a post (title, body, tag) into the db
def posts_insert(post, user_id):
    # check when the user last posted
    query = "SELECT * FROM posts WHERE user_id=" + str(user_id) + ";"
    user_posts = select_all(query, ())

    if len(user_posts) != 0:
        user_posts.sort(reverse=True, key=lambda x: datetime.strptime(x[3] + " " + x[4], "%d/%m/%Y %H:%M"))

        # get the last posts date and time
        last_date = datetime.strptime(user_posts[0][3], "%d/%m/%Y")
        last_time = datetime.strptime(user_posts[0][4], "%H:%M")

        # check if last post on same day
        if(last_date.date() == datetime.now().date()):
            # check time since last post
            time_diff =  (datetime.now() - last_time).seconds/60
            if(time_diff < 5):
                # last post less than 5 mins ago, dont post
                return False, "Sorry we can't post this right now, try again later"


    # find post_id based on last post in db
    all_posts = select_all("SELECT * FROM posts;", ())
    post_id = all_posts[len(all_posts)-1][0] + 1

    # get current date and time
    date = datetime.now().strftime("%d/%m/%Y")
    time = datetime.now().strftime("%H:%M")

    # get tag id
    tag_id = tags_get_id(post[2])

    Utilities.use_encoding = True
    # parse the title and body
    title = Utilities.parse(post[0])[1]
    body = Utilities.parse(post[1])[1]

    # create post with all parameters
    insert_post = (post_id, title, body, date, time, tag_id, user_id)

    # sql query to execute
    sql_query = "INSERT INTO posts(post_id, title, body, date, time, tag_id, user_id) VALUES(?, ?, ?, ?, ?, ?, ?)"

    inserted = insert(sql_query, insert_post)
    if(inserted):
        return inserted, "New post made :)", post_id
    else:
        return inserted, "Sorry we can't post this right now, try again later"

# delete a post given the id
def posts_delete(id):
    sql_query = "DELETE FROM posts WHERE post_id=?"
    return delete(sql_query, (id,))

# get a single post with all its comments
def posts_get_single(post_id, username):
    #[Title, date, time, post text, username, post_id, logged in, [comments]]
    sql_query = "SELECT title, date, time, body, user_id, post_id FROM posts where post_id=?"
    post = select_one(sql_query, (post_id,))
    if post is None:
        return []
    post_username = users_get_username(post[4])
    full_post = [Utilities.unencode(post[0]), post[1], post[2], Utilities.unencode(post[3]), post_username, post[5], post_username == username, []]
    comments = comments_from_post(post_id)
    for comment in comments:
        comment.append(comment[1] == username)

    full_post[7] = comments
    return full_post





# get the name of a tag given the id
def tags_get_name(id):
    sql_query = "SELECT * FROM tags WHERE tag_id=?"
    row = select_one(sql_query, (id,))
    if row is not None:
        return row[1]
    else:
        return None

# get the id of a tag given the name
def tags_get_id(name):
    sql_query = "SELECT * FROM tags WHERE name=?"
    row = select_one(sql_query, (name,))
    if row is not None:
        return row[0]
    else:
        return None

# get all the tag names from the db
def tags_get_all_names():
    names =  select_all("SELECT name FROM tags;", ())
    ret = []
    for name in names:
        ret.append(name[0])
    return ret



# select all the comments from a specific post
def comments_from_post(post_id):
    sql_query = "SELECT * FROM comments WHERE post_id=?"
    parameters = (post_id,)
    comments = select_all(sql_query, parameters)
    full_comments = []
    if comments is not None:
        for comment in comments:
            username = users_get_username(comment[5])
            user = users_get_details(username)
            full_comments.append([user[1], username, comment[1], comment[2], comment[3], comment[0]])
    full_comments.sort(reverse=True, key=lambda x: datetime.strptime(x[3] + " " + x[4], "%d/%m/%Y %H:%M"))
    return full_comments

# add a comment (comment, post_id, user_id) into the db
def comments_insert(comment):
    # check when the last comment was inserted by this user
    # get them in date order

    all_comments = select_all("SELECT * FROM comments where user_id=?;", (str(comment[2])))
    if all_comments is not None:

        all_comments.sort(reverse=True, key=lambda x: datetime.strptime(x[2] + " " + x[3], "%d/%m/%Y %H:%M"))
        # get the last posts date and time
        last_date = datetime.strptime(all_comments[0][2], "%d/%m/%Y")
        last_time = datetime.strptime(all_comments[0][3], "%H:%M")
        # check if last post on same day
        if (last_date.date() == datetime.now().date()):
            # check time since last post
            time_diff = (datetime.now() - last_time).seconds / 60
            if (time_diff < 2):
                # last post less than 5 mins ago, dont post
                return False


    sql_query = "INSERT INTO comments(comment_id, comment, date, time, post_id, user_id) VALUES (?, ?, ?, ?, ?, ?);"
    all_comments= select_all("SELECT * FROM comments;", ())
    comment_id = all_comments[len(all_comments) - 1][0] + 1


    # parse comment text before adding
    body = Utilities.parse(comment[0])[1]

    # check that post id and user id are valid
    post = select_one("SELECT * FROM posts WHERE post_id=?", (comment[1],))
    user = users_get_username(comment[2])
    if (user is None) or (post is None):
        # either is not valid, don't insert
        return False


    # get current date and time
    date = datetime.now().strftime("%d/%m/%Y")
    time = datetime.now().strftime("%H:%M")

    insert_comment = (comment_id, body, date, time, comment[1], comment[2])
    return insert(sql_query, insert_comment)

# delete a comment from the db
def comments_delete(id):
    sql_query = "DELETE FROM comments WHERE comment_id=?"
    return delete(sql_query, (id,))



# log user into the application
# returns bool and message
def login(email, password):
    user_ok = False
    pass_ok = False

    # parse email, if not valid set to "" as extra protection
    if not Utilities.is_email(email):
        email = ""

    # search for username
    user = users_search_user(email)
    if(user == email):
        user_ok = True

    # search for password (even if username incorrect)
    hash_pword = users_get_password(email)
    if hash_pword is None:
        hash_pword = ""
    added = users_get_added(email)
    if added is None:
        added = datetime.now()
    else:
        added = datetime.strptime(added, "%d/%m/%Y %H:%M:%S:%f")
    salt = users_get_salt(email)
    if salt is None:
        salt = ""
    readFile = Utilities.readFile("pepper.txt")
    pepper = Utilities.decrypt(readFile[0], datetime.strptime(readFile[1], "%d/%m/%Y %H:%M:%S:%f"))
    hash_input = Utilities.hash(pepper+password+salt, added)
    pass_ok = Utilities.compare_hashes(hash_pword, hash_input)

    # check if both correct
    # make sure error message is generic
    if(user_ok and pass_ok):
        return True, "Log in successful :)"
    else:
        return False, "Error logging in :("

# sign up to the applicaion
# returns bool and message
def signUp(email, username, password):
    flash_message = False
    message = ""
    # check if email is valid
    if not Utilities.is_email(email):
        flash_message = True
        message = "Please enter a valid email address!"
    # check if password is valid
    elif not Utilities.secure_password(password):
        flash_message = True
        message = "Please enter a more secure password!"
    else:
        # parse the username- reject if not accepted
        accepted, username = Utilities.parse(username)
        if not accepted:
            flash_message = True
            message = "Please enter a valid username!"
        # search for username on DB
        result = users_get_email(username)
        if result is not None:
            flash_message = True
            message = "That username is already taken!"


    if(flash_message):
        # if any of the fields are invalid, send flash message
        return False, message

    message = None
    user_inserted = False
    # password, email and username are valid
    # check if email already linked to an account
    result = users_search_user(email)
    if result is not None:
        # email linked to account
        sendEmail(email, [username, EMAIL_EXISTS])
    else:
        # create a new user
        user_inserted = users_insert((email, username, password))
        if user_inserted:
            # send email if user has been inserted
            sendEmail(email, [username, USER_CREATE])
        else:

            message = "Sorry! Unable to sign up at this time, please try again later"

    if message is None:
        message = "An email has been sent to " + email + " please check your inbox for details!"
    return user_inserted, message

# send email given email address and content (username, message)
def sendEmail(address, content):
    sender = 'Brickin\' it! <email>'

    email = MIMEMultipart('alternative')
    email['From'] = sender
    email['To'] = address
    email['Subject'] = "Brickin' it"


    text = "Hi there {username}!\n {message}".format(username = content[0], message = content[1])

    html = """\
    <html>
    <head></head>
    <body>
        <h3>Hi there {username}!</h3>
        <p>{message}</p> 
    </body>
    </html>
    """.format(username = content[0], message = content[1])


    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    email.attach(part1)
    email.attach(part2)

    list = Utilities.readFile("pass.txt")
    list[1] = datetime.strptime(list[1], "%d/%m/%Y %H:%M:%S:%f")
    password = Utilities.decrypt(list[0], list[1])
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login("group08.studyplanner@gmail.com", password)
        server.send_message(email)
        server.close()
    except smtplib.SMTPException as e:
        print("ERROR: ")
        print(e)
       # server.close()
        return False
    return True

# search the db for a specific term
def search(term):
    Utilities.extra_secure = True
    term = Utilities.parse(term)[1]
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

    return term, rows



if __name__ == '__main__':
    users_insert(("a", "a", "a"))

