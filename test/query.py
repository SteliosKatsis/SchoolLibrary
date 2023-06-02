import mysql.connector
import sys

connection = mysql.connector.connect(
host = 'localhost',
user = 'root',
password = 'Stelios.181002',
database = 'website'
)

if connection.is_connected():
    print("Connection was successful")
else:
    print("Connection failed")
    sys.exit(1)


# Create a cursor object to interact with the database
cursor = connection.cursor()

# Execute an SQL query
query = "Select school_name from school"
cursor.execute(query)

# Fetch all rows from the result set
school_names = cursor.fetchall()

for row in school_names:
    school_name = row[0] 
    print(school_name)


# Close the database connection
connection.close()
print("Database connection closed")
