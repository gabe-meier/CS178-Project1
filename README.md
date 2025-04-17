# City Finder Web App

## Project Summary

City Finder is a Flask-based web application that allows users to create, log into, or delete accounts. After logging in, users can submit preferences for a city they want to visit—population range, countries, or continents—and receive a list of matching cities. User data is stored in DynamoDB, while city data is queried from a MySQL RDS instance.

## Technologies Used

- **Flask** (Python web framework)  
- **HTML** (Frontend)  
- **AWS EC2** (App hosting)  
- **AWS DynamoDB** (User data storage)  
- **AWS RDS (MySQL)** (City data storage)  
- **Bootstrap & Select2** (Frontend styling and enhanced form elements)

## Set Up and Run Instructions
The app can be accessed through a web brower using the URL http://54.91.128.25:8080/

Alternatively, you can run the app on your local machine with your own RDS instance
1. In a terminal type `git clone https://github.com/gabe-meier/CS178-Project1`
2. Change directory into the cloned folder using `cd CS178-Project1`
3. Create a creds.py file in the folder with credentials for an RDS server with the world data base installed
4. Run the flaskapp.py file using `nohup python3 flaskapp.py &`
5. Connect in a web browser using http://127.0.0.1:8080/


