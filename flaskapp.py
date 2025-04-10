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

def display_html(rows):
    html = ""
    html += """<table><tr><th>Name</th></tr>"""

    for r in rows:
        html += "<tr><td>" + str(r[0]) + "</td><td>"
    html += "</table></body>"
    return html

@app.route("/viewdb")
def viewdb():
    rows = execute_query("""SELECT name FROM city
                Limit 5""")
    return display_html(rows)

# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)