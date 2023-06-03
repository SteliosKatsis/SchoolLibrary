import os
from flask import Flask, request, redirect, url_for, render_template, session, flash
import mysql.connector
import sys

app = Flask(__name__, static_folder='static')

# Generate a secret key or provide your own
secret_key = os.urandom(24)
app.secret_key = secret_key

def get_database_connection():
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
        
    return connection


# ------------------------Login-------------------------- #

@app.route('/')
def initial():
    return redirect(url_for('go_to_login'))



@app.route('/login')
def go_to_login():
    return render_template('login.html')



@app.route('/signup')
def go_to_signup():
    return render_template('signup.html')



@app.route('/signup', methods = ['POST'])
def signup():
    # Create a new database connection for this request
    connection = get_database_connection()

    # Retrieve the form data
    username = request.form.get('username')
    new_password = request.form.get('new-password')
    first_name = request.form.get('first-name')
    last_name = request.form.get('last-name')
    age = request.form.get('age')
    school = request.form.get('school')
    role = request.form.get('role')

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    args = (school, username, new_password, first_name, last_name, age, role)
    cursor.callproc('InsertUser', args)

    # Commit the changes to the database
    connection.commit()

    # Close the cursor and database connection
    cursor.close()

    connection.close()
    print("Database connection closed")

    return redirect(url_for('go_to_login'))



@app.route('/login', methods=['POST'])
def login():
    # Retrieve the form data
    username = request.form.get('username')
    password = request.form.get('password')

    # Create a new database connection for this request
    connection = get_database_connection()

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    cursor.execute(
        "SELECT first_name, last_name, age, approval_status, role, school_id, user_id "
        "FROM User WHERE username = %s AND password = %s", 
        (username, password))

    result = cursor.fetchone()
    print(result)

    if result is not None:
        # User is authenticated
        first_name = result[0]
        last_name = result[1]
        age = result[2]
        approval_status = result[3]
        role = result[4]
        school_id = result[5]
        user_id = result[6]

        if approval_status == "Approved":

            # Store all the user's information for all the time they are logged in
            session['username'] = username
            session['password'] = password
            session['first_name'] = first_name
            session['last_name'] = last_name
            session['age'] = age
            session['approval_status'] = approval_status
            session['role'] = role
            session['school_id'] = school_id
            session['user_id'] = user_id

            if role == 'Administrator':
                # Redirect to the administrator page
                return redirect(url_for('admin'))

            query = "SELECT school_name FROM School WHERE school_id = %s"
            params = [school_id]
            cursor.execute(query, params)

            res = cursor.fetchone()
            session['school_name'] = res[0]
            
            if role == 'Operator':
                # Redirect to the operator page
                return redirect(url_for('operator_homepage'))
            
            else:
                return redirect(url_for('user'))
            
        else:
            return render_template('login.html', approval_status = approval_status)

    else:
        # Redirect to a page indicating that the user is pending approval
        return redirect(url_for('pending_approval_page'))
    
    
    
@app.route('/user_homepage')
def user():
    return render_template('home.html')



@app.route('/admin_homepage')
def admin():
    return render_template('administrator.html')


# ----------------------------User----------------------------------- #

@app.route('/edit_personal_info')
def edit_personal_info():

    return render_template(
        'change_info.html', 
        username = session.get('username'),
        password = session.get('password'),
        first_name = session.get('first_name'),
        last_name = session.get('last_name'),
        school_name = session.get('school_name'),
        role = session.get('role')
        )



@app.route('/update_info', methods=['POST'])
def update_info():
    # Retrieve the form data
    user_id = session.get('user_id')
    new_username = request.form.get('username')
    new_password = request.form.get('password')
    new_first_name = request.form.get('first-name')
    new_last_name = request.form.get('last-name')
    new_school = request.form.get('school')

    # Create a new database connection for this request
    connection = get_database_connection()

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    cursor.callproc('UpdateUser',
    (user_id, new_school, new_username, new_password, new_first_name, new_last_name))

    # Commit the changes to the database
    connection.commit()

    # Close the cursor and database connection
    cursor.close()
    connection.close()
    print("Database connection closed")

    my_message = "User info has been updated successfully."

    # Redirect to the home page or appropriate page after updating personal information
    # return redirect(url_for('home_page'))

    return render_template('home.html', message = my_message)


# --------------------------Operator--------------------------------- #

@app.route('/operator_homepage')
def operator_homepage():
    return render_template('operator_homepage.html')



@app.route('/operator_books', methods=['POST'])
def operator_books():
    available_books = request.form.get('available_books')   # button press
    title = request.form.get('title')
    author = request.form.get('author')
    copies = request.form.get('copies')
    category = request.form.get('categories')
    choice = request.form.get('choice')
    
    school_id = session.get('school_id')

    # Upper button clicked
    if(available_books == 'books'):
        choice =  'books'

    # Nothing pressed
    if(choice is None):
        return redirect(url_for('operator_homepage'))
    
    # Create a new database connection for this request
    connection = get_database_connection()

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    if choice == 'books':
        query = "SELECT * FROM Book WHERE school_id = %s"
        params = [school_id]
        cursor.execute(query, params)
    elif choice == 'category':
        query = "SELECT * FROM Book JOIN Category ON Category.book_id = Book.book_id WHERE school_id = %s AND category_name = %s"
        params = [school_id, category]
        cursor.execute(query, params)
    elif choice == 'author':
        query = "SELECT * FROM Book JOIN Author ON Author.book_id = Book.book_id WHERE school_id = %s AND author_name = %s"
        params = [school_id, author]
        cursor.execute(query, params)
    elif choice == 'copies':
        query = "SELECT * FROM Book WHERE school_id = %s AND available_copies = %s"
        params = [school_id, copies]
        cursor.execute(query, params)
    elif choice == 'title':
        query = "SELECT * FROM Book WHERE school_id = %s AND title = %s"
        params = [school_id, title]
        cursor.execute(query, params)

    column_names = [i[0] for i in cursor.description]
    books = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]
    cursor.close()
    
    # cursor = connection.cursor()
    # query = "SELECT Author.author_name FROM Book JOIN Author ON Author.book_id = Book.book_id WHERE school_id = %s"
    # params = [school_id]
    # cursor.execute(query, params)
    # print(cursor.fetchall())
    # cursor.close()

    return render_template('operator_books.html',
    choice = choice, title = title, author = author, copies = copies, category = category, books = books)



@app.route('/operator_borrowed')
def operator_borrowed():    
    school_id = session.get('school_id')
    
    # Create a new database connection for this request
    connection = get_database_connection()

    # Create a cursor object to interact with the database

    cursor = connection.cursor()
    query = """SELECT b.*, r.loan_date, r.return_date, r.return_date > NOW()
    AS del FROM (Reservation AS r) JOIN (Book AS b) ON r.book_id=b.book_id
    WHERE b.school_id = %s AND (r.reservation_status = 'Borrowed' OR r.reservation_status='Delayed')"""
    params = [school_id]
    cursor.execute(query, params)
    column_names = [i[0] for i in cursor.description]
    books = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]
    cursor.close()

    return render_template('operator_borrowed.html', books = books)



@app.route('/operator_reserved')
def operator_reserved():
    return render_template('operator_reserved.html')



@app.route('/approval')
def approval():
    return render_template('approval.html')



@app.route('/operator_reviews')
def operator_reviews():
    school_id = session.get('school_id')
    
    connection = get_database_connection()
    cursor = connection.cursor()
    query = """SELECT u.*, r.comment, r.rating, r.review_id FROM (Review AS r)
    JOIN (User AS u) ON u.user_id=r.user_id WHERE u.school_id = %s
    AND r.approval_status = 'Pending'"""
    params = [school_id]
    cursor.execute(query, params)
    column_names = [i[0] for i in cursor.description]
    pending = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]
    cursor.close()
    
    return render_template('operator_reviews.html', pending_users = pending)

@app.route('/operator_reviews', methods=['POST'])
def operator_reviews_new():
    approval = request.form.get('approve')
    decline = request.form.get('decline')
    
    connection = get_database_connection()
    cursor = connection.cursor()
    
    review_id = 0
    if(approval is not None):
        review_id = approval
        query = "UPDATE Review SET approval_status = 'Approved' WHERE review_id = %s"
    elif(decline is not None):
        review_id = decline
        query = "UPDATE Review SET approval_status = 'Rejected' WHERE review_id = %s"
    
    params = [review_id]
    cursor.execute(query, params)
    cursor.close()
    
    return redirect(url_for('operator_reviews'))


# ----------------------Error Pages------------------ #

@app.route('/logout')
def logout():
    # Clear the session variables
    session.clear()

    # Redirect to the login page
    return redirect(url_for('login'))



@app.route('/pending_approval')
def pending_approval_page():
    # Code to render the pending approval page
    return render_template('pending_approval.html')



@app.route('/error')
def error_page():
    # Code to render the error page
    return render_template('error.html')


# ----------------------Run-------------------------- #

if __name__ == '__main__':
    app.run(port=5000, debug=True)