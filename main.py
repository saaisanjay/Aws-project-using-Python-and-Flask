from flask import Flask, render_template, request
import sqlite3 as sql
import pandas as pd
app = Flask(__name__)
import sqlite3, csv
from math import sin , cos , sqrt, atan2 , radians
from pandas import DataFrame
from sklearn.cluster import KMeans
import os

#this is used for uploading csv file
@app.route('/csvfile', methods=['GET','POST'])
def csvfile():
    if request.method == 'POST':
        file = request.files['csv']
        data = pd.read_csv(file)
        con = sql.connect('projectdatabase.db')
        #table name and replace if any update
        data.to_sql(name="mytable", con=con, if_exists="replace", index=False)
        #display the details in home page
        return render_template('home.html')
print ("Operation done successfully");

#for displaying all the rows and columns from the table
@app.route('/list')
def list():
    con = sql.connect("projectdatabase.db")
    #connection to the database
    con.row_factory = sql.Row
    #connection to the server
    cur = con.cursor()
    cur.execute("select * from mytable")
    rows = cur.fetchall();
    #displaying the result in a html file
    return render_template("list.html", rows=rows)

#decorator used for finding the magnitude for the given query
@app.route('/first',methods=['GET','POST'])
def first():
    con = sql.connect("projectdatabase.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    #query to get the magnitude from the user and display
    cur.execute("select COUNT(mag) From mytable WHERE mag>?",(request.form['magu'],))
    rows = cur.fetchone();
    return render_template("firstresult.html", rows=rows)

#function/decorator for finding time and magnitude query
@app.route('/second', methods=['GET','POST'])
def second():
    con = sql.connect("projectdatabase.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    #query to select rows and columns for the query
    cur.execute("select * from mytable WHERE (mag>=? AND mag<=?) AND (time BETWEEN '2018-06-01T23:42:06.350Z' AND '2018-06-08T23:33:25.750Z')",(request.form['magstart'],(request.form['magend'])))
    rows = cur.fetchall();
    return render_template("secondresult.html", rows=rows)

#function/decoratorfor finding latitude and longitude
@app.route('/third', methods=['GET','POST'])
def third():
    R = 6373.0
    #input the latitude and longitude for the given question and convert them to radians
    latitude1 = radians(19.4211674)
    longitude1 = radians(-155.2793274)
    con = sql.connect("projectdatabase.db")
    con.row_factory = sql.Row
    cursor = con.cursor()
    #select longitude and latitudefrom table
    cursor.execute("select latitude, longitude from mytable")
    rows = cursor.fetchall()
    dist = []
    for row in rows:
        latitude0 = row[0]
        longitude0 = row[1]
        latitude2 = radians(row[0])
        longitude2 = radians(row[1])
        distlon = longitude2 - longitude1
        distlat = latitude2 - latitude1
        #formula to calculate the distance for the given latitude and longitude
        #ref link given below for the formula
        a = sin(distlat / 2) ** 2 + cos(latitude1) * cos(latitude2) * sin(distlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        if distance < 50:
            cursor.execute("select * from mytable where latitude = ? AND longitude = ?",(latitude0,longitude0))
            con.row_factory = sql.Row
            rows = cursor.fetchall()
            dist.append(rows)
    return render_template('thirdresult.html',dist=dist)
#https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude

#function/decoratorfor clusteringusing kmeans
@app.route('/fourth')
def fourth():
    con = sql.connect("projectdatabase.db")
    con.row_factory = sql.Row
    cursor = con.cursor()
    #select longitude and latitude
    cursor.execute("select latitude, longitude from mytable")
    rows = cursor.fetchall()
    #put the data as DataFrame
    X = DataFrame(rows)
    estimator = KMeans(n_clusters=5)
    #fit the data using kmeans clustering
    estimator.fit(X)
    labels = estimator.predict(X)
    C = estimator.cluster_centers_
    #print result
    return render_template('fourthresult.html',data=C)
#https://mubaris.com/2017/10/01/kmeans-clustering-in-python/

#function/decoratorto find night time earthquake occurances
@app.route('/five', methods=['GET','POST'])
def five():
    con = sql.connect("projectdatabase.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * From mytable WHERE mag>=? " ,(request.form['mag'],))
    rows = cur.fetchall();
    #create a list to store output data
    list1 = []
    for night in rows:
        #split the time given from table
        x1=night[0].split("T")[1]
        #again split to get the hours alone
        y1=x1.split(":")[0]
        if int(y1)<6 or int(y1)>=20:
            #append to the list
            list1.append(night)
        result1=len(list1)

        #same procedure for day/morning
    list2=[]
    for morning in rows:
        x2=morning[0].split("T")[1]
        y2=x2.split(":")[0]
        if int(y2)>6 and int(y2)<=20:
            list2.append(morning)
        result2=len(list2)
    return render_template("fiveresult.html",msg=result1, msg1=result2)


@app.route('/')
def home():
    return render_template("home.html")

@app.route('/firstform')
def firstform():
    return render_template("firstform.html")

@app.route('/secondform')
def secondform():
    return render_template("secondform.html")

@app.route('/fiveform')
def fiveform():
    return render_template("fiveform.html")

#to get the file size of the current working directory 
@app.route('/size')
def size():
    Assignment2=os.getcwd()
    size=os.path.getsize(Assignment2)
    return render_template("sizeresult.html" ,size=size)

if __name__ == '__main__':
    app.run(debug=True)
