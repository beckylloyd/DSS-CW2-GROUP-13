import csv
import json
import locale
import os
import calendar
import random
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

# CAPTCHA DETAILS
# img number, x min, x max, y min, y max
captchaCoords = {1: [230, 260, 39, 67],
                 2: [40, 65, 105, 136],
                 3: [138, 164, 267, 292],
                 4: [73, 100, 266, 291],
                 5: [266, 292, 136, 165],
                 6: [200, 228, 9, 37],
                 7: [170, 195, 10, 36],
                 8: [72, 98, 42, 67],
                 9: [38, 65, 237, 260],
                 10: [104, 131, 138, 164]}
numberOfImages = random.randint(1, 10)
imageNumbers = []

mail = ''

app.secret_key = os.urandom(32)

# Sets locale to GB for currency
locale.setlocale(locale.LC_ALL, 'en_GB')


@app.before_request
def make_session_permanent():
    now = datetime.now()
    if session.get("userid") is not None:
        session['urls'].append(request.url)
        try:
            last_active = session['last_active']
            # print(last_active)
            delta = now - last_active
            if delta.seconds > 600:
                session['last_active'] = now
                flash(
                    "Your session has expired due to 10 minutes of inactivity, please sign back in to access your account. ",
                    "warning")
                session.pop('userid', None)
                session.pop('username', None)
                session.pop('bio', None)
                session.pop('image', None)
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
        global captchaComplete
        context = {}
        request.context = context
        if 'userid' not in session or 'userid' in session is None:
            context['loggedIn'] = False
        else:
            context['loggedIn'] = True
            context['username'] = session['username']
            context['userid'] = session['userid']
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
        comments = len(DBConnect.comments_from_post(post[0]))
        userImage = DBConnect.users_get_details(username)[1]
        posts.append([post[0], title, body, userImage, username, tag, datetime, comments])

    starWarsPosts = []
    ninjago = []
    city = []
    friends = []
    for post in posts:
        if 'Star' in post[5]:
            starWarsPosts.append(post)
        if 'Ninjago' in post[5]:
            ninjago.append(post)
        if 'City' in post[5]:
            city.append(post)
        if 'Friends' in post[5]:
            friends.append(post)

    context['rows'] = posts
    return render_template('index.html', **context)


# search for a post
@app.route('/search', methods=['GET'])
@std_context
def search():
    context = request.context
    search_term = request.args["search_term"]
    posts = []
    results = DBConnect.search(search_term)

    # postid, tritle, body, date, time, tag, username

    for post in results[1]:
        username = post[6]
        tag = post[5]
        datetime = post[3] + " " + post[4]
        title = Utilities.unencode(post[1])
        body = Utilities.unencode(post[2])
        comments = len(DBConnect.comments_from_post(post[0]))
        userImage = DBConnect.users_get_details(username)[1]
        posts.append([post[0], title, body, userImage, username, tag, datetime, comments])

    # for item in results[1]:
    #     datetime = item[3] + " " + item[4]
    #     title = Utilities.unencode(item[1])
    #     body = Utilities.unencode(item[2])
    #     posts.append([title, body, item[6], item[5], datetime])
    context['search_term'] = results[0]
    context['rows'] = posts
    return render_template('searchResults.html', **context)


# log in to application
@app.route('/logIn')
@std_context
def logIn():
    context = request.context
    if context['loggedIn']:
        flash("Oops you need to log out to view that page!", "warning")
        return redirect('/')

    return render_template('logIn.html', **context)


@app.route('/userLogIn', methods=['GET', 'POST'])
@std_context
def userLogIn():
    global mail
    context = request.context

    context['message'] = ""
    if 'userid' not in session or session['userid'] is None:
        email = request.form['email']
        password = request.form['password']
        result = DBConnect.login(email, password)
        if not result[0]:
            flash("Error logging in, please try again.", "danger")

        if result[0]:
            mail = email
            setCaptcha()
            session['urls'] = []
            return render_template('captcha.html', **context)
    else:
        flash("Oops, a user is already logged in!")

    return render_template('logIn.html', **context)


def setCaptcha():
    global numberOfImages
    global imageNumbers
    numberOfImages = random.randint(1, 5)
    imageNumbers = random.sample(range(1, 11), numberOfImages)


@app.route('/getCaptcha', methods=['GET', 'POST'])
@std_context
def getCaptcha():
    global mail
    global imageNumbers

    if imageNumbers:
        return json.dumps({'status': 'OK', 'image': imageNumbers.pop(0)});
    else:
        session['userid'] = DBConnect.users_get_id(mail)
        session['username'] = DBConnect.users_get_username(session['userid'])
        session['image'] = DBConnect.users_get_details(session['username'])[1]
        session['bio'] = DBConnect.users_get_details(session['username'])[2]
        return json.dumps({'status': 'all captcha complete'})


@app.route('/validateCaptcha', methods=['GET', 'POST'])
@std_context
def validateCaptcha():
    global captchaCoords

    imageNumber = int(request.form['imageNumber'])
    x = int(request.form['x'])
    y = int(request.form['y'])
    xCorrect = False
    yCorrect = False

    coordArray = captchaCoords[imageNumber]

    if coordArray[0] <= x <= coordArray[1]:
        xCorrect = True

    if coordArray[2] <= y <= coordArray[3]:
        yCorrect = True

    if xCorrect and yCorrect:
        return json.dumps({'status': 'OK'})
    else:
        return json.dumps({'status': 'validation failed'})


# logs out user from session, called from log out button
@app.route('/signUp')
@std_context
def signUp():
    context = request.context
    if context['loggedIn']:
        flash("Oops you need to log out to view that page!", "warning")
        return redirect('/')
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
    else:

        flash("Oops! Looks like your already logged in!", "warning")
        return redirect("/")
    # check if sign up was successful or not
    if result[0]:
        flash(result[1], "success")
        return redirect("/")
    else:
        flash(result[1], "warning")

    return render_template('signUp.html', **context)


@app.route('/userLogOut')
@std_context
def userLogOut():
    session.pop('userid', None)
    session.pop('username', None)
    session.pop('bio', None)
    session.pop('image', None)
    return redirect("/logIn")


# used in session auto log out modal to update last active in python
@app.route('/ajaxLogOut', methods=['GET', 'POST'])
@std_context
def ajaxLogOut():
    session.pop('userid', None)
    session.pop('username', None)
    session.pop('bio', None)
    session.pop('image', None)
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


@app.route('/specificPost/<int:postID>')
@std_context
def specificPost(postID):
    # [Title, date, time, post text, username, post_id, logged in, [comments]]
    context = request.context

    if context['loggedIn']:
        username = session['username']
    else:
        username = ""

    context['item'] = DBConnect.posts_get_single(postID, username)

    if context['item']:
        context['posterUsername'] = context['item'][4]
        context['image'] = DBConnect.users_get_details(context['item'][4])[1]
        return render_template('specificPost.html', **context)
    else:
        error_page(404)


# my profile
@app.route('/profile')
@std_context
def profile():
    context = request.context
    if not context['loggedIn']:
        flash("Oops you need to log in to view that page!", "warning")
        return redirect('/')

    # Get user details
    results = DBConnect.users_get_details(session['username'])
    context['username'] = results[0]
    context['image'] = results[1]
    context['bio'] = results[2]

    # Get post details into array of arrays - given the username into database method
    all_posts = DBConnect.posts_from_user(results[0])  # [Title, date, time, post text, username, post_id]

    # Single array contain [Title, date, time, post text, username, post_id]

    # for each loop to append the 'boolean' value to end of each post array (checking if the username is the user that is logged in)
    for each in all_posts:
        each.append(True)  # [Title, date, time, post text, username, post_id, logged in]

        # for each loop to append array of array of comments to end of each post array
        comments = DBConnect.comments_from_post(each[5])

        # for each loop in each comment to check if boolean of if user name = logged in user
        for comment in comments:
            if (comment[1] == context['username']):
                comment.append(True)
            else:
                comment.append(False)
        each.append(comments)

    context['list'] = all_posts
    context['myProfile'] = True
    return render_template('profile.html', **context)


# other profile
@app.route('/otherProfile/<string:username>')
@std_context
def otherProfile(username):
    context = request.context

    # Get user details
    results = DBConnect.users_get_details(username)
    context['username'] = results[0]
    context['image'] = results[1]
    context['bio'] = results[2]

    # Get post details into array of arrays - given the username into database method
    all_posts = DBConnect.posts_from_user(results[0])  # [Title, date, time, post text, username, post_id]

    # Single array contain [Title, date, time, post text, username, post_id]
    if context['loggedIn']:
        sessionUsername = session['username']
    else:
        sessionUsername = ""
    # for each loop to append the 'boolean' value to end of each post array (checking if the username is the user that is logged in)
    for each in all_posts:

        if (username == sessionUsername):
            each.append(True)  # [Title, date, time, post text, username, post_id, logged in]
        else:
            each.append(False)
        # for each loop to append array of array of comments to end of each post array
        comments = DBConnect.comments_from_post(each[5])

        # for each loop in each comment to check if boolean of if user name = logged in user
        for comment in comments:

            if (comment[1] == sessionUsername):
                comment.append(True)
            else:
                comment.append(False)
        each.append(comments)

    context['list'] = all_posts
    context['myProfile'] = False
    return render_template('profile.html', **context)


@app.route('/commentsBox', methods=['GET', 'POST'])
@app.route('/otherProfile/commentsBox', methods=['GET', 'POST'])
@app.route('/specificPost/commentsBox', methods=['GET', 'POST'])
@std_context
def commentsBox():
    context = request.context
    try:
        urlToGet = 2
        last_url = session['urls'][len(session['urls']) - urlToGet]
        while "static" in last_url:
            urlToGet += 1
            last_url = session['urls'][len(session['urls']) - urlToGet]
    except:
        last_url = None

    post_id = None
    add = False
    delete = False

    try:
        post_id = request.form['add']
        add = True
        comment = request.form['comment']
        added = DBConnect.comments_insert((comment, post_id, context['userid']))
        if added:
            flash("Comment added successfully!", "info")
        else:
            flash("Sorry, that comment couldn't be posted at this time, try again later", "danger")
    except:
        add = False

    try:
        post_id = request.form['delete']
        delete = True
        deleted = DBConnect.posts_delete(post_id)
        if deleted:
            flash("Post deleted succesfully!", "info")
        else:
            flash("Sorry that post could not be deleted at this time, try again later", "danger")
    except:
        delete = False

    if delete != add and last_url is not None:
        if delete and "specificPost" in last_url:
            return redirect('/')
        return redirect(last_url)
    else:
        flash("Uh oh! Something has gone wrong :(", "danger")
        return redirect("/")


@app.route('/deleteComment', methods=['GET', 'POST'])
@app.route('/otherProfile/deleteComment', methods=['GET', 'POST'])
@app.route('/specificPost/deleteComment', methods=['GET', 'POST'])
@std_context
def deleteComment():
    context = request.context
    try:
        last_url = session['urls'][len(session['urls']) - 2]
    except:
        last_url = None

    value = request.form['delComment']
    try:
        DBConnect.comments_delete(value)
        flash("Comment deleted sucessfully!", "info")
    except:
        flash("Sorry, this comment could not be deleted at this time", "danger")
    if last_url is not None:
        return redirect(last_url)
    else:
        return redirect("/")


@app.route('/changeImage/<image>', methods=['POST'])
@std_context
def changeImage(image):
    try:
        DBConnect.users_update_image(session['username'], image)
        flash("Profile picture updated", "success")
    except:
        flash("Sorry, unable to update your picture right now!", "info")

    return redirect('/profile')


@app.route('/updateBio', methods=['POST'])
@std_context
def updateBio():
    value = request.form['bio']
    try:
        DBConnect.users_update_bio(session['username'], value)
        flash("Bio updated", "success")
    except:
        flash("Sorry, unable to update your bio right now!", "info")
    return redirect('/profile')

@app.errorhandler(400)  # Bad request
@app.errorhandler(401)  # Unauthorized
@app.errorhandler(403)  # Forbidden
@app.errorhandler(404)  # Not found
@app.errorhandler(405)  # Method not allowed
@app.errorhandler(408)  # Request time-out
@app.errorhandler(500)  # Server error
@std_context
def error_page(error):
    context = request.context
    return render_template('error.html', **context)


if __name__ == '__main__':
    app.run()
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='strict',
    )

