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

    username = request.form['username']
    password = request.form['password']
    result = DBConnect.login(username, password)

    return render_template('logIn.html', message=result[1])


# create a new post
@app.route('/newPost')
def newPost():
    return render_template('newPost.html')

# search for a post
@app.route('/search')
def search():
    return render_template('searchResults.html')


if __name__ == '__main__':
    app.run()
