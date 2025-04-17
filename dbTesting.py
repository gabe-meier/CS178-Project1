# Code to test connection to SQL databse
import pymysql
import creds 

def mysqlconnect():
    # To connect MySQL database
    conn = pymysql.connect(
        host= creds.host,
        user= creds.user, 
        password = creds.rds_password,
        db=creds.db,
        )
    cur = conn.cursor()

    # Practice query to test connection
    cur.execute("""SELECT DISTINCT name from country ORDER BY name""")
    output = cur.fetchall()
    
    # Print Results formatted like the html I needed for the country list
    # I copied this output into the html file so I didn't have to manually type an option for each country
    for row in output:
        print('<option value="'+row[0]+'">'+row[0]+'</option>')
      
    # To close the connection
    conn.close()
  
# Driver Code
if __name__ == "__main__" :
    mysqlconnect()