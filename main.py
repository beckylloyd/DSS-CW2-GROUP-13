import csv
import locale
import os
import calendar
from functools import wraps
from flask import Flask, render_template, make_response, session, redirect
from flask import request
from datetime import datetime
from datetime import timedelta

import DBConnect
app = Flask(__name__)

# Sets date and time format
dateFormat = '%d/%m/%Y'
dateTimeFormat = dateFormat + " %H:%M"

app.secret_key = os.urandom(32)

# Sets locale to GB for currency
locale.setlocale(locale.LC_ALL, 'en_GB')



def std_context(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        context = {}
        request.context = context
        if 'userid' in session:
            context['loggedIn'] = True
            context['username'] = session['username']
        else:
            context['loggedIn'] = False
        return f(*args, **kwargs)

    return wrapper


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
@std_context
# Function to return homepage
def index():
    context = request.context
    allPosts = DBConnect.posts_get_all()
    posts = []
    for post in allPosts:
        username = DBConnect.users_get_username(post[6])
        tag = DBConnect.tags_get_name(post[5])
        datetime = post[3] + " " + post[4]
        posts.append([post[1], post[2], username, tag, datetime])
    context['rows'] = posts
    return render_template('index.html', **context)


# log in to application
@app.route('/logIn')
@std_context
def logIn():
    context = request.context
    return render_template('logIn.html', **context)


@app.route('/userLogIn', methods=['GET', 'POST'])
@std_context
def userLogIn():
    context = request.context

    context['message'] = ""
    if 'userid' not in session or session['userid'] is None:
        email = request.form['email']
        password = request.form['password']
        result = DBConnect.login(email, password)
        context['message'] = result[1]
        if result[0]:
            session['userid'] = DBConnect.users_get_id(email)
            session['username'] = DBConnect.users_get_username(session['userid'])
            return redirect('/')
    else:
        context['message'] = "User already logged in :("

    return render_template('logIn.html', **context)

@app.route('/signUp')
@std_context
def signUp():
    context = request.context
    return render_template('signUp.html', **context)


@app.route('/userSignUp', methods=['GET', 'POST'])
@std_context
def userSignUp():
    context = request.context

    context['message'] = ""
    if 'userid' not in session or session['userid'] is None:
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        result = DBConnect.signUp(email, username, password)
        context['message'] = result[1]
    else:
        context['message'] = "User already logged in :("

    return render_template('signUp.html', **context)

@app.route('/userLogOut')
def userLogOut():
    session.pop('userid', None)
    session.pop('username', None)
    return redirect('/')


# show new post page
@app.route('/newPost')
@std_context
def newPost():
    context = request.context
    # populate the dropdown with all tag names
    context['tag_values'] = DBConnect.tags_get_all_names()
    return render_template('newPost.html', **context)


# create a new post
@app.route('/makeNewPost', methods=['GET', 'POST'])
@std_context
def makeNewPost():
    context = request.context
    msg = ""
    # get data from form
    title = request.form['title']
    body = request.form['body']
    tag = request.form['tag']

    # check the user is logged in
    if (session['userid'] is not None):
        # check all inputs are filled
        # TODO disable submit button instead, and highlight the box to be filled
        if (tag == "default" or title == "" or str.isspace(title) or body == "" or str.isspace(body)):
            context['msg1'] = "Please make sure all boxes are filled :)"
        else:
            DBConnect.posts_insert((title, body, tag), session['userid'])
            context['msg1'] = "new post made :D"
    else:
        context['msg1'] = "Sorry, you need to be logged in to post :'("

    # get tags to make sure the select box is populated
    context['tag_values'] = DBConnect.tags_get_all_names()
    return render_template('newPost.html', **context)


# search for a post
@app.route('/search', methods=['GET'])
@std_context
def search():
    context = request.context
    search_term = request.args["search_term"]
    posts = []
    results = DBConnect.search(search_term)
    for item in results:
        datetime = item[3] + " " + item[4]
        posts.append([item[1], item[2], item[6], item[5],datetime ])
    context['search_term'] = search_term
    context['rows'] = posts
    return render_template('searchResults.html', **context)



if __name__ == '__main__':
    app.run()
