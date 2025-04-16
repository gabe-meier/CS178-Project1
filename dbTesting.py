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

    # Execute Query
    cur.execute("""SELECT DISTINCT name from country ORDER BY name""")
    output = cur.fetchall()
    
    # Print Results
    for row in output:
        print('<option value="'+row[0]+'">'+row[0]+'</option>')
      
    # To close the connection
    conn.close()
  
# Driver Code
if __name__ == "__main__" :
    mysqlconnect()