from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash

import pymysql
import creds 

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def hello():
    return '<h2>Hello from Flask!</h2>'

def get_conn():
    conn = pymysql.connect(
        host= creds.host,
        user= creds.user, 
        password = creds.rds_password,
        db=creds.db,
        )
    return conn

def execute_query(query, args=()):
    cur = get_conn().cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows



min_pop = 100000
max_pop = 2000000
continent = ("Asia", "Africa", "North America", "South America", "Antartica", 
             "Europe", "Oceania")
country = ("Germany", "Italy")

# Made an "Ugly" table by coping code from lab 13, had ChatGPT make it pretty
# Had ChatGPT show me how to turn it into a template
@app.route("/viewdb")
def viewdb():
    rows = execute_query("""SELECT city.name as City, country.name as Country, city.population as Population
                FROM city, country WHERE city.countrycode = country.code
                AND city.population > %s AND city.population < %s
                AND country.continent in %s
                AND country.name in %s
                Order by RAND()
                Limit 15""", (str(min_pop), str(max_pop), continent, country))

    return render_template("viewdb.html", rows=rows)

@app.route("/timequerytextbox", methods = ['GET'])
def time_form():
  return render_template('textbox.html', fieldname = "Country")

@app.route("/timequerytextbox", methods = ['POST'])
def time_form_post():
    text = request.form['text']
    return viewdb(text)

# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)