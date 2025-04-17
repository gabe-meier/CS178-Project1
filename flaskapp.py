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

# Connect to dynamo db table
TABLE_NAME = "Users"

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)


# Render home page for base URL
@app.route('/')
def hello():
    return render_template("home.html")


# Function to create a new account
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        # Extract form data
        # User must enter username and password of account they want to create
        username = request.form['username']
        password = request.form['password']
        # Check if the username already exists
        if dynamofunctions.user_exists(username):
            # If user exists already, let the user know the account already exists and have them try again
            flash('Username already exists, try again.', 'warning')
            return redirect(url_for('create_account'))
        else:
            # If username does not exist, create account
            dynamofunctions.create_user(username,password)
            flash('User Created Successfully!', 'success')
            # Bring user to the page for them to submit city preferences
            return redirect(url_for('country_form', username=username))

    else:
        # Render the create user page if the request method is GET
        return render_template('createuser.html')  



# Function for user to log in to an existing account
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Extract form data
        # User must enter username and password of account they want to log into
        username = request.form['username']
        password = request.form['password']
        # Check to see if username exists
        if dynamofunctions.user_exists(username):
            # Check to see if password matches
            if dynamofunctions.check_password(username,password):
                try:
                    # Check to see if user has already submitted their city preferences
                    response = table.get_item(Key={'Username': username})  
                    if 'Continents' not in response['Item']:
                        pref = False
                    else:
                        pref = True 
                except ClientError as e:
                    pref = False
                # If statement testing to see if user has submitted preferences
                if pref:
                    # Get the user's previously stored preferences for city size, country, and continent
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
                    # Direct user to page with city results
                    return redirect(f"/{username}/countryresults?{full_query}")
                else:
                    # If user has not submitted preferences, direct them to the page to submit preferences
                    flash('Logged in Successfully!', 'success')
                    return redirect(url_for('country_form', username=username))
            else:
                # If the user got their password incorrect let them know and have them try again
                flash('Password incorrect, try again.', 'warning')
                return redirect(url_for('login'))
        else:
            # If username does not exist, let them know and have them try again
            flash('Username does not exist. did you mean to create a new account?', 'warning')
            return redirect(url_for('login'))
    else:
        # Render the log in page if the request method is GET
        return render_template('login.html')

# Function for use to delete an account
@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        # Extract form data
        # User must enter username and password of account they want to delete
        username = request.form['username']
        password = request.form['password']
        # Check to see if the user exists
        if dynamofunctions.user_exists(username):
            # Check if the password is correct for the user
            if dynamofunctions.check_password(username, password):
                # If password is correct, delete the user and bring them back to the home page
                dynamofunctions.delete_user(username)
                flash('User Deleted Successfully!', 'success')
                return redirect(url_for('hello'))
            else:
                # If the password does not match username tell user to try again
                flash('Password incorrect, try again.', 'warning')
                return redirect(url_for('delete_account'))
        else:
            # If username does not exist tell user to try again
            flash('User does not exist, try again.', 'warning')
            return redirect(url_for('delete_account'))

    else:
        # Render the delete user page if the request method is GET
        return render_template('deleteuser.html')  

# Connect to SQL server with the world database
def get_conn():
    conn = pymysql.connect(
        host= creds.host,
        user= creds.user, 
        password = creds.rds_password,
        db=creds.db,
        )
    return conn

# Function to execute SQL queries
def execute_query(query, args=()):
    cur = get_conn().cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows


# Function to get a list of cities that fit user's criteria
#Had ChatGPT show my how to pass arguments from the textbox into here,
#For some reason couldn't get the code from lab 13 to work the same
def get_city_data(min_pop, max_pop, continents=None, countries=None):
    # Query for if the user specified cerrtain countries they want to visit
    if countries:
        # Placeholder for the query so it includes specified countries
        country_placeholders = ','.join(['%s'] * len(countries))
        # Query selects cities joining with the country table to display more info about the cities
        query = f"""SELECT city.name AS City, country.name AS Country, city.population AS Population,
                    country.continent AS Continent, city.district AS District
                    FROM city
                    JOIN country ON city.countrycode = country.code
                    WHERE city.population >= %s AND city.population <= %s
                    AND country.name IN ({country_placeholders})
                    ORDER BY RAND()
                    LIMIT 10"""
        # Parameters specifying size of city and country
        params = (min_pop, max_pop, *countries)
    else:
        #Query for if the user did not specify countries, but did specify continents
        if continents:
            # Placeholder for the query so it includes specified continents
            continent_placeholders = ','.join(['%s'] * len(continents))
            # Query selects cities joining with the country table to display more info about the cities
            query = f"""SELECT city.name AS City, country.name AS Country, city.population AS Population,
                    country.continent AS Continent, city.district AS District
                    FROM city
                    JOIN country ON city.countrycode = country.code
                    WHERE city.population >= %s AND city.population <= %s
                    AND country.continent IN ({continent_placeholders})
                    ORDER BY RAND()
                    LIMIT 10"""
            # Parameters specifying size of city and continent
            params = (min_pop, max_pop, *continents)
        else:
            # Query for if user did not specify continent or country
            query = f"""SELECT city.name AS City, country.name AS Country, city.population AS Population,
                    country.continent AS Continent, city.district AS District
                    FROM city
                    JOIN country ON city.countrycode = country.code
                    WHERE city.population >= %s AND city.population <= %s
                    ORDER BY RAND()
                    LIMIT 10"""
            # Parameter to specify size of city
            params = (min_pop, max_pop)
    # return the results of the correct query
    return execute_query(query, params)

# Renders the preference form for a specific user
@app.route("/<username>/countryquery", methods = ['GET'])
def country_form(username):
  return render_template('textbox.html', fieldname = "Country")

# Get the data user entered about their preferences
@app.route("/<username>/countryquery", methods=['POST'])
def country_form_post(username):
    # Get the form data
    countries = request.form.getlist('countries')
    continents = request.form.getlist('continents')
    pop_range = request.form.get('pop_range')
    if not pop_range:
        return redirect(url_for('country_form', username=username))
    # Store preferences in dynamoDB table
    dynamofunctions.update_pop_range(username, pop_range)
    dynamofunctions.update_countries(username, countries)
    dynamofunctions.update_continents(username, continents)
    # Encode countries and continents as query parameters
    # ChatGPT helped me format in a way so that they could be passed into the SQL query
    country_query = '&'.join([f"countries={urllib.parse.quote(c)}" for c in countries])
    continent_query = '&'.join([f"continents={urllib.parse.quote(c)}" for c in continents])
    pop_query = f"pop_range={pop_range}"

    # Build full query string including population range, continents, and countries
    # ChatGPT helped me create a url that changes for multiple selected countries
    full_query = f"{pop_query}&{country_query}&{continent_query}"
    return redirect(f"/{username}/countryresults?{full_query}")


@app.route("/<username>/countryresults")
def viewcities(username):
    # ChatGPT helped me figure out how to pass the list of countries into this function
    pop_range = request.args.get('pop_range')
    countries = request.args.getlist('countries')
    continents = request.args.getlist('continents')
    # Splut population range into minimum and maximum population
    try:
        min_pop, max_pop = map(int, pop_range.split('-'))
    except (ValueError, AttributeError):
        return "Invalid or missing population range", 400
    # get_city_data gives us a list of cities that fit user's criteria
    rows = get_city_data(min_pop, max_pop, continents, countries)
    # Render the template that shows user the cities
    return render_template("viewdb.html", rows=rows, username=username)


# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)