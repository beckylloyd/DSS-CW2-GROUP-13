import csv
import locale
import calendar
from flask import Flask, render_template
from flask import request
from datetime import datetime
from datetime import timedelta

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
    return render_template('index.html')


@app.route('/logIn')
# Function to return homepage
def logIn():
    return render_template('logIn.html')

if __name__ == '__main__':
    app.run()
