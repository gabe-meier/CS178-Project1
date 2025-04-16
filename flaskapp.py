from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
import urllib.parse #ChatGPT had me install this package to make url redirecting work
import pymysql
import creds 
import boto3
from botocore.exceptions import ClientError
import dynamofunctions

app = Flask(__name__)
app.secret_key = 'your_secret_key'

TABLE_NAME = "Users"

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)



@app.route('/')
def hello():
    return render_template("home.html")

@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        password = request.form['password']
        if dynamofunctions.user_exists(username):
            if dynamofunctions.check_password(username, password):
                dynamofunctions.delete_user(username)
                flash('User Deleted Successfully!', 'success')
                return redirect(url_for('hello'))
            else:
                flash('Password incorrect, try again.', 'warning')
                return redirect(url_for('delete_account'))
        else:
            flash('User does not exist, try again.', 'warning')
            return redirect(url_for('delete_account'))

    else:
        # Render the form page if the request method is GET
        return render_template('deleteuser.html')  

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        password = request.form['password']
        if dynamofunctions.user_exists(username):
            if dynamofunctions.check_password(username,password):
                try:
                    # Check if the movie exists
                    response = table.get_item(Key={'Username': username})  
                    if 'Continents' not in response['Item']:
                        pref = False
                    else:
                        pref = True 
                except ClientError as e:
                    pref = False
                if pref:
                    continents = dynamofunctions.get_continents(username)
                    countries = dynamofunctions.get_countries(username)
                    pop_range = dynamofunctions.get_pop_range(username)
                    # Encode countries and continents as query parameters
                    country_query = '&'.join([f"countries={urllib.parse.quote(c)}" for c in countries])
                    continent_query = '&'.join([f"continents={urllib.parse.quote(c)}" for c in continents])
                    pop_query = f"pop_range={pop_range}"

                    # Build full query string
                    full_query = f"{pop_query}&{country_query}&{continent_query}"
                    flash('Logged in Successfully!', 'success')
                    return redirect(f"/{username}/countryresults?{full_query}")
                else:
                    flash('Logged in Successfully!', 'success')
                    return redirect(url_for('country_form', username=username))
            else:
                flash('Password incorrect, try again.', 'warning')
                return redirect(url_for('login'))
        else:
            flash('Username does not exist. did you mean to create a new account?', 'warning')
            return redirect(url_for('login'))
    else:
        # Render the form page if the request method is GET
        return render_template('login.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        password = request.form['password']
        if dynamofunctions.user_exists(username):
            flash('Username already exists, try again.', 'warning')
            return redirect(url_for('create_account'))
        else:
            dynamofunctions.create_user(username,password)
            flash('User Created Successfully!', 'success')
            return redirect(url_for('country_form', username=username))

    else:
        # Render the form page if the request method is GET
        return render_template('createuser.html')  



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



#Had ChatGPT show my how to pass arguments from the textbox into here,
#For some reason couldn't get the code from lab 13 to work the same
def get_city_data(min_pop, max_pop, continents=None, countries=None):
    if countries:
        country_placeholders = ','.join(['%s'] * len(countries))
        query = f"""SELECT city.name AS City, country.name AS Country, city.population AS Population,
                    country.continent AS Continent, city.district AS District
                    FROM city
                    JOIN country ON city.countrycode = country.code
                    WHERE city.population > %s AND city.population < %s
                    AND country.name IN ({country_placeholders})
                    ORDER BY RAND()
                    LIMIT 10"""
        params = (min_pop, max_pop, *countries)
    else:
        if continents:
            continent_placeholders = ','.join(['%s'] * len(continents))
            query = f"""SELECT city.name AS City, country.name AS Country, city.population AS Population,
                    country.continent AS Continent, city.district AS District
                    FROM city
                    JOIN country ON city.countrycode = country.code
                    WHERE city.population > %s AND city.population < %s
                    AND country.continent IN ({continent_placeholders})
                    ORDER BY RAND()
                    LIMIT 10"""
            params = (min_pop, max_pop, *continents)
        else:
            query = f"""SELECT city.name AS City, country.name AS Country, city.population AS Population,
                    country.continent AS Continent, city.district AS District
                    FROM city
                    JOIN country ON city.countrycode = country.code
                    WHERE city.population > %s AND city.population < %s
                    ORDER BY RAND()
                    LIMIT 10"""
            params = (min_pop, max_pop)
    
    return execute_query(query, params)

@app.route("/<username>/countryquery", methods = ['GET'])
def country_form(username):
  return render_template('textbox.html', fieldname = "Country")

# ChatGPT helped me create a url that changes for multiple selected countries
@app.route("/<username>/countryquery", methods=['POST'])
def country_form_post(username):
    countries = request.form.getlist('countries')
    continents = request.form.getlist('continents')
    pop_range = request.form.get('pop_range')
    if not pop_range:
        return redirect(url_for('country_form', username=username))

    dynamofunctions.update_pop_range(username, pop_range)
    dynamofunctions.update_countries(username, countries)
    dynamofunctions.update_continents(username, continents)
    # Encode countries and continents as query parameters
    country_query = '&'.join([f"countries={urllib.parse.quote(c)}" for c in countries])
    continent_query = '&'.join([f"continents={urllib.parse.quote(c)}" for c in continents])
    pop_query = f"pop_range={pop_range}"

    # Build full query string
    full_query = f"{pop_query}&{country_query}&{continent_query}"
    return redirect(f"/{username}/countryresults?{full_query}")

# ChatGPT helped me figure out how to pass the list of countries into this function
@app.route("/<username>/countryresults")
def viewcities(username):
    pop_range = request.args.get('pop_range')
    countries = request.args.getlist('countries')
    continents = request.args.getlist('continents')

    try:
        min_pop, max_pop = map(int, pop_range.split('-'))
    except (ValueError, AttributeError):
        return "Invalid or missing population range", 400

    rows = get_city_data(min_pop, max_pop, continents, countries)
    print(len(rows))
    return render_template("viewdb.html", rows=rows, username=username)


# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)