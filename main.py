import csv
import locale
import calendar
from flask import Flask, render_template
from flask import request
from datetime import datetime
from datetime import timedelta

import DBConnect
app = Flask(__name__)

# Sets date and time format
dateFormat = '%d/%m/%Y'
dateTimeFormat = dateFormat + " %H:%M"

# Sets locale to GB for currency
locale.setlocale(locale.LC_ALL, 'en_GB')

# id of the current user
# TODO make more secure
user_id = None


# Function to read a csv file, add each row into a list and return the list
def readFile(aFile):
    with open(aFile, 'r') as inFile:
        reader = csv.reader(inFile)
        aList = [row for row in reader]
    return aList


# Function to write to a list and save back to csv file
def writeFile(aList, aFile):
    with open(aFile, 'w', newline='') as outFile:
        writer = csv.writer(outFile)
        writer.writerows(aList)
    return


# Sets default route to homepage
@app.route('/')
# Sets route '/home' to homepage
@app.route('/home')
# Function to return homepage
def index():
    allPosts = DBConnect.posts_get_all()
    posts = []
    for post in allPosts:
        username = DBConnect.users_get_username(post[6])
        tag = DBConnect.tags_get_name(post[5])
        datetime = post[3] + " " + post[4]
        posts.append([post[1], post[2], username, tag, datetime])

    cols = ["Title", "Body", "Username", "Tag", "Posted On"]
    return render_template('index.html', col_names = cols, rows = posts)


# log in to application
@app.route('/logIn')
def logIn():
    return render_template('logIn.html')

@app.route('/userLogIn', methods=['GET', 'POST'])
def userLogIn():
    global user_id
    message = ""
    if(user_id is None):
        username = request.form['username']
        password = request.form['password']
        result = DBConnect.login(username, password)
        message = result[1]
        if(result[0]):
            user_id = DBConnect.users_get_id(username)
    else:
        message = "User already logged in :("
    print(user_id)
    return render_template('logIn.html', message=message)

# show new post page
@app.route('/newPost')
def newPost():
    # populate the dropdown with all tag names
    tags = DBConnect.tags_get_all_names()
    return render_template('newPost.html', tag_values = tags)

# create a new post
@app.route('/makeNewPost', methods=['GET', 'POST'])
def makeNewPost():
    msg = ""
    # get data from form
    title = request.form['title']
    body = request.form['body']
    tag = request.form['tag']

    # check the user is logged in
    if(user_id is not None):
        # check all inputs are filled
        # TODO disable submit button instead, and highlight the box to be filled
        if (tag == "default" or title == "" or str.isspace(title) or body == "" or str.isspace(body)):
            msg = "Please make sure all boxes are filled :)"
        else:
            DBConnect.posts_insert((title, body, tag), user_id)
            msg = "new post made :D"
    else:
        msg = "Sorry, you need to be logged in to post :'("

    # get tags to make sure the select box is populated
    tags = DBConnect.tags_get_all_names()
    return render_template('newPost.html', tag_values=tags, msg1=msg)

# search for a post
@app.route('/search')
def search():
    return render_template('searchResults.html')


if __name__ == '__main__':
    app.run()
