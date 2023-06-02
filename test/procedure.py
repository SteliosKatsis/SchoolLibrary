import mysql.connector
import sys

connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='192123George',
    database='website'
)

if connection.is_connected():
    print("Connection was successful")
else:
    print("Connection failed")
    sys.exit(1)

# Create a cursor object to interact with the database
cursor = connection.cursor()

args = ('George Seretakos School', 'Ilekktras 52', 'Dionysos', '6909653954', 'g.seretakos@gmail.com', 'Stelios Katsis')  # Example arguments
cursor.callproc('InsertSchool', args)

# Commit the changes to the database
connection.commit()

# Close the cursor and database connection
cursor.close()
connection.close()
print("Database connection closed")
