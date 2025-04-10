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

# Made an "Ugly" table by coping code from lab 13, had ChatGPT make it pretty
def display_html(rows):
    html = """
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 30px;
                background-color: #f9f9f9;
            }
            table {
                border-collapse: collapse;
                width: 60%;
                margin: auto;
                background-color: #fff;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            th, td {
                text-align: left;
                padding: 12px 15px;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #007BFF;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            h2 {
                text-align: center;
                color: #333;
            }
        </style>
    </head>
    <body>
        <h2>15 Most Populous Cities</h2>
        <table>
            <tr><th>City</th><th>Country</th><th>Population</th></tr>
    """

    for r in rows:
        html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>"

    html += """
        </table>
    </body>
    </html>
    """
    return html

@app.route("/viewdb")
def viewdb():
    rows = execute_query("""SELECT city.name as City, country.name as Country, city.population as Population 
                FROM city, country WHERE city.countrycode = country.code
                Order by city.population desc
                Limit 15""")
    return display_html(rows)

# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)