import boto3
from botocore.exceptions import ClientError

TABLE_NAME = "Users"

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)


def create_user(username,password):
    table.put_item(
         Item={
        'Username': username,
        'Password': password
        }
    )

def update_pop_range(username, pop_range):
    table.update_item(
        Key = {"Username": username}, 
        UpdateExpression = "SET Pop_range = :val1", 
        ExpressionAttributeValues = {':val1': pop_range}
    )

def update_countries(username, countries):
    table.update_item(
        Key = {"Username": username}, 
        UpdateExpression = "SET Countries = :val1", 
        ExpressionAttributeValues = {':val1': countries}
    )

def update_continents(username, continents):
    table.update_item(
        Key = {"Username": username}, 
        UpdateExpression = "SET Continents = :val1", 
        ExpressionAttributeValues = {':val1': continents}
    )

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
        
def check_password(username,password):
    response = table.get_item(Key={'Username': username})
    user = response.get("Item")
    password_c = user["Password"]
    if password == password_c:
        return True
    else:
        return False

def get_pop_range(username):
    response = table.get_item(Key={'Username': username})
    user = response.get("Item")
    return user["Pop_range"]

def get_countries(username):
    response = table.get_item(Key={'Username': username})
    user = response.get("Item")
    return user["Countries"]

def get_continents(username):
    response = table.get_item(Key={'Username': username})
    user = response.get("Item")
    return user["Continents"]

def delete_user(username):
    table.delete_item(Key = {"Username": username})