from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
import urllib.parse #ChatGPT had me install this package to make url redirecting work
import pymysql
import creds 

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def hello():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        password = request.form['password']
        print(username,password)
        flash('Logged in added successfully!', 'success')  # 'success' is a category; makes a green banner at the top
        # Redirect to home page or another page upon successful submission
        return redirect(url_for('country_form'))
    else:
        # Render the form page if the request method is GET
        return render_template('login.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        password = request.form['password']
        print(username,password)
        
        flash('User Created Successfully!', 'success')  # 'success' is a category; makes a green banner at the top
        # Redirect to home page or another page upon successful submission
        return redirect(url_for('country_form'))
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

@app.route("/countryquery", methods = ['GET'])
def country_form():
  return render_template('textbox.html', fieldname = "Country")

# ChatGPT helped me create a url that changes for multiple selected countries
@app.route("/countryquery", methods=['POST'])
def country_form_post():
    countries = request.form.getlist('countries')
    continents = request.form.getlist('continents')
    pop_range = request.form.get('pop_range')
    if not pop_range:
        return redirect(url_for('country_form'))

    # Encode countries and continents as query parameters
    country_query = '&'.join([f"countries={urllib.parse.quote(c)}" for c in countries])
    continent_query = '&'.join([f"continents={urllib.parse.quote(c)}" for c in continents])
    pop_query = f"pop_range={pop_range}"

    # Build full query string
    full_query = f"{pop_query}&{country_query}&{continent_query}"
    return redirect(f"/countryresults?{full_query}")

# ChatGPT helped me figure out how to pass the list of countries into this function
@app.route("/countryresults")
def viewcities():
    pop_range = request.args.get('pop_range')
    countries = request.args.getlist('countries')
    continents = request.args.getlist('continents')

    try:
        min_pop, max_pop = map(int, pop_range.split('-'))
    except (ValueError, AttributeError):
        return "Invalid or missing population range", 400

    rows = get_city_data(min_pop, max_pop, continents, countries)
    print(len(rows))
    return render_template("viewdb.html", rows=rows)


# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)