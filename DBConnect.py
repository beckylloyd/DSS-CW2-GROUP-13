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

import Utilities
DATABASE = r"sqlite.db"

EMAIL_EXISTS = "You already have an account with this email address! Please log in to continue!"
USER_CREATE = "You have sucessfully made an account! Please log in to continue!"


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

def update_authoriser(sqltype, arg1, arg2, dbname, source):
    if sqltype == sqlite3.SQLITE_READ or sqltype == sqlite3.SQLITE_TRANSACTION or sqltype == sqlite3.SQLITE_UPDATE:
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

def update(sql_query, parameters):
    try:
        # get a db connection
        conn = connect()
        # set authoriser to insert only
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

def users_get_id_u(username):
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
        return row[2]
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
        return row[3]
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
        return row[1]
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
        return row[1]
    return None
"""
gets specific details of a user 
username: username of user to search 

return: (username, image, bio)
"""
def users_get_details(username):
    sql_query = "SELECT username, image, bio FROM users WHERE username=?"
    parameters = (username,)
    return select_one(sql_query, parameters)


"""
get the date a user was added to the db
email: email of the user to search 

return: date that user was added
"""
def users_get_added(email):
    sql_query = "SELECT * FROM users WHERE email=?"
    parameters = (email,)
    row = select_one(sql_query, parameters)
    if (row is not None):
        return row[4]
    return None

"""
select all users from the DB

return: all rows found
"""
def users_get_all():
    return select_all("SELECT * FROM users;", ())

"""
insert one user into the DB
user: data to insert (email, username, password)
"""
def users_insert(user):
    sql_query = "INSERT INTO users(user_id, email, username, password, added) VALUES(?, ?, ?, ?, ?);"
    all_users = users_get_all()
    id = all_users[len(all_users) -1][0] + 1
    added = datetime.now()
    hashed = Utilities.hash(user[2], added)
    insert_user = (id, user[0], user[1], hashed, added.strftime("%d/%m/%Y %H:%M:%S:%f"))
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
update the bio of a specific user
username: username of user to update
bio: new bio to insert

return bool is updates
"""
def users_update_bio(username, bio):
    user_id = users_get_id_u(username)
    sql_query = "UPDATE users SET bio=? WHERE user_id=?"
    parameters = (bio, user_id)
    return update(sql_query, parameters)

"""
update the image of a specific user
username: username of user to update
image: new image to insert

return bool is updates
"""
def users_update_image(username, image):
    user_id = users_get_id_u(username)
    sql_query = "UPDATE users SET image=? WHERE user_id=?"
    parameters = (image, user_id)
    return update(sql_query, parameters)


"""
select all posts in the db

returns: list of all posts 
"""
def posts_get_all():
    posts = select_all("SELECT * FROM posts;", ())
    posts.sort(reverse = True, key=lambda x:datetime.strptime(x[3] + " " + x[4], "%d/%m/%Y %H:%M"))
    return posts

"""
get all posts from specific user
username: username of user to search

return: list of posts [post_id, title, body, date, time, tag_id, user_id]
"""
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
"""
insert post into the db
post: post t insert (title, body, tag)
user_id: id of user currently logged in
"""
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
        return False, "Sorry we can't post this right now, try again later"
    finally:
        if conn:
            conn.close()
    return True, "New post made :)"


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
    names =  select_all("SELECT name FROM tags;", ())
    ret = []
    for name in names:
        ret.append(name[0])
    return ret

"""
selects all comments from post
post_id = post to search

return list of comments[image, user name, comment, date, time]
"""
def comments_from_post(post_id):
    sql_query = "SELECT * FROM comments WHERE post_id=?"
    parameters = (post_id,)
    comments = select_all(sql_query, parameters)
    full_comments = []
    if comments is not None:
        for comment in comments:
            username = users_get_username(comment[5])
            user = users_get_details(username)
            full_comments.append([user[1], username, comment[1], comment[2], comment[3]])
    return full_comments

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

    # parse email, if not valid set to "" as extra protection
    if not Utilities.is_email(email):
        email = ""

    # search for username
    user = users_search_user(email)
    if(user == email):
        user_ok = True

    # search for password (even if username incorrect)
    hash_pword = users_get_password(email)
    added = users_get_added(email)
    if added is None:
        added = datetime.now()
    else:
        added = datetime.strptime(users_get_added(email), "%d/%m/%Y %H:%M:%S:%f")
    hash_input = Utilities.hash(password, added)
    if (hash_input == hash_pword):
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
            message = "Please enter a valid username"
        # search for username on DB
        result = users_get_email(username)
        if result is not None:
            flash_message = True
            message = "That username is already taken"


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
        print("sent!")
    except smtplib.SMTPException as e:
        print("ERROR: ")
        print(e)
       # server.close()
        return False
    return True

"""
search the db
term: user input from the search bar

returns: term after parsing, posts found matching the term
"""
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



# if __name__ == '__main__':
#     # print(users_get_details("billy"))
#     # print(posts_from_user("billy"))
#     # print(comments_from_post(1))
#     print(users_update_bio("billy", "I love lego so much!!"))
#     print(users_update_image("billy", "LEGO_PIRATE"))