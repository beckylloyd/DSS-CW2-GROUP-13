import csv
import json
import locale
import os
import calendar
from functools import wraps
from flask import Flask, render_template, make_response, session, redirect, app, flash
from flask import request
from datetime import datetime
from datetime import timedelta

import DBConnect
import Utilities
app = Flask(__name__)

# Sets date and time format
dateFormat = '%d/%m/%Y'
dateTimeFormat = dateFormat + " %H:%M"

app.secret_key = os.urandom(32)

# Sets locale to GB for currency
locale.setlocale(locale.LC_ALL, 'en_GB')

@app.before_request
def make_session_permanent():
    now = datetime.now()
    if session.get("userid") is not None:
        try:
            last_active = session['last_active']
            print(last_active)
            delta = now - last_active
            if delta.seconds > 600:
                session['last_active'] = now
                flash(
                    "Your session has expired due to 10 minutes of inactivity, please sign back in to access your account. ",
                    "warning")
                session.pop('userid', None)
                session.pop('username', None)
                return redirect("/logIn")
        except:
            pass

    try:
        session['last_active'] = now
    except:
        pass


def std_context(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        context = {}
        request.context = context
        if 'userid' not in session or 'userid' in session is None:
            context['loggedIn'] = False
        else:
            context['loggedIn'] = True
            context['username'] = session['username']
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
        title = Utilities.unencode(post[1])
        body = Utilities.unencode(post[2])
        posts.append([title, body, username, tag, datetime])
    context['rows'] = posts
    return render_template('index.html', **context)


# log in to application
@app.route('/logIn')
@std_context
def logIn():
    context = request.context
    if context['loggedIn']:
        flash("Oops you need to log out to view that page!", "warning")
        return redirect('/')

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
        if not result[0]:
            flash("Error logging in, please try again.", "danger")

        if result[0]:
            session['userid'] = DBConnect.users_get_id(email)
            session['username'] = DBConnect.users_get_username(session['userid'])
            return redirect('/')
    else:
        flash("Oops, a user is already logged in!")

    return render_template('logIn.html', **context)

# logs out user from session, called from log out button
@app.route('/signUp')
@std_context
def signUp():
    context = request.context
    if context['loggedIn']:
        flash("Oops you need to log out to view that page!", "warning")
        return redirect('/')

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
        flash("Please sign out to create a new account.")

    return render_template('signUp.html', **context)

@app.route('/userLogOut')
@std_context
def userLogOut():
    session.pop('userid', None)
    session.pop('username', None)
    return redirect("/logIn")

# used in session auto log out modal to update last active in python
@app.route('/ajaxLogOut', methods=['GET', 'POST'])
@std_context
def ajaxLogOut():
    session.pop('userid', None)
    session.pop('username', None)
    flash("Your session has expired due to 10 minutes of inactivity, please sign back in to access your account. ",
          "warning")
    return json.dumps({'status': 'OK',
                       'message': "Your session has expired due to 10 minutes of inactivity, please sign back in to access your account."});


# used in session auto log out modal to update last active in python
@app.route('/ajaxExtend', methods=['GET', 'POST'])
@std_context
def ajaxExtend():
    return json.dumps({'status': 'OK', 'message': "session extended"});

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
            res = DBConnect.posts_insert((title, body, tag), session['userid'])
            context['msg1'] = res[1]
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
    for item in results[1]:
        datetime = item[3] + " " + item[4]
        title = Utilities.unencode(item[1])
        body = Utilities.unencode(item[2])
        posts.append([title, body, item[6], item[5], datetime])
    context['search_term'] = results[0]
    context['rows'] = posts
    return render_template('searchResults.html', **context)


# my profile
@app.route('/profile')
@std_context
def profile():
    context = request.context
    if not context['loggedIn']:
        flash("Oops you need to log in to view that page!", "warning")
        return redirect('/')

    context = request.context

    # Get user details
    # array of [image text name, user name, bio] (SHOULD BE ABLE TO ADD THIS INTO LOG IN SO ITS SAVED IN THE SESSION)
    context['username'] = "username"
    context['image'] = "LEGO_PIRATE"
    context['bio'] = "This is a bio about someone who really loves LEGO. Like really loves LEGO."

    # Get post details into array of arrays - given the username into database method
    # Single array contain [Title, date, time, post text, username, post_id]
    # for each loop to append the 'boolean' value to end of each post array (checking if the username is the user that is logged in)
    # for each loop to append array of array of comments to end of each post array
    # Single array contains [image text name, user name, comment, date, time]
    # for each loop in each comment to check if boolean of if user name = logged in user

    context['list'] = [["TITLE", "01/01/2021", "12:54pm",
                        "POST TEXT", "username", True,
                        [["LEGO_NURSE", "commenter_name", False, "comment", "01/01/21", "10:00am"],
                         ["LEGO_Pirate", "username", True, "comment back", "01/01/21", "10:07am"]]]
                       ]
    return render_template('profile.html', **context)


# other profile
@app.route('/otherProfile')
@std_context
def otherProfile(username):
    context = request.context

    # get user details based on username
    # results = DBConnect.getUserdetails(username)
    # context['username'] = results[1]
    # context['image'] = results[2]
    # context['bio'] = results[3]

    return render_template('profile.html', **context)





if __name__ == '__main__':
    app.run()
