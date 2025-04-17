# This file has important functions for dynamo db CRUD capability
import boto3
from botocore.exceptions import ClientError

#Specify the dynamoDB table we want to work with
TABLE_NAME = "Users"

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)

# Function to create a new user
def create_user(username,password):
    table.put_item(
         Item={
        'Username': username,
        'Password': password
        }
    )

# Function to update a user's preferred population range
def update_pop_range(username, pop_range):
    table.update_item(
        Key = {"Username": username}, 
        UpdateExpression = "SET Pop_range = :val1", 
        ExpressionAttributeValues = {':val1': pop_range}
    )

# Function to update a user's preferred countries
def update_countries(username, countries):
    table.update_item(
        Key = {"Username": username}, 
        UpdateExpression = "SET Countries = :val1", 
        ExpressionAttributeValues = {':val1': countries}
    )

# Function to update a user's preferred continents
def update_continents(username, continents):
    table.update_item(
        Key = {"Username": username}, 
        UpdateExpression = "SET Continents = :val1", 
        ExpressionAttributeValues = {':val1': continents}
    )

# Function returns true is a username exists in the database, false if it does not
def user_exists(username):
    lock_is_on = True
    while lock_is_on == True:
        try:
            # Check if the movie exists
            response = table.get_item(Key={'Username': username})  
            if 'Item' not in response:
                return False
            else:
                return True

        except ClientError as e:
            return False

# Function to check if a username matches a password
# Important to only use usernames we know exist, or else there will be an error
# in flaskapp.py I made sure all usernames exist before running this function 
def check_password(username,password):
    response = table.get_item(Key={'Username': username})
    user = response.get("Item")
    password_c = user["Password"]
    if password == password_c:
        return True
    else:
        return False

# Function to get a user's preferred population range given their username
def get_pop_range(username):
    response = table.get_item(Key={'Username': username})
    user = response.get("Item")
    return user["Pop_range"]

# Function to get a user's preferred countries given their username
def get_countries(username):
    response = table.get_item(Key={'Username': username})
    user = response.get("Item")
    return user["Countries"]

# Function to get a user's preferred continents given their username
def get_continents(username):
    response = table.get_item(Key={'Username': username})
    user = response.get("Item")
    return user["Continents"]

# Function to delete a user
def delete_user(username):
    table.delete_item(Key = {"Username": username})