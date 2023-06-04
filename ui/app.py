import os
from flask import Flask, request, redirect, url_for, render_template, session, flash
import mysql.connector
import sys
import datetime

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

# ----------------------Delete Functions----------------------- #

def DeleteUser(user_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT reservation_id FROM Reservation WHERE user_id = %s", (user_id,))
    res_id = list()
    while(True):
        x = cursor.fetchone()
        if x is None: break
        res_id.append(x[0])
        
    cursor.execute("SELECT review_id FROM Review WHERE user_id = %s", (user_id,))
    rev_id = list()
    while(True):
        x = cursor.fetchone()
        if x is None: break
        rev_id.append(x[0])
        
    for i in res_id:
       # Call the stored procedure
        cursor.callproc('DeleteReservation', (i,))
        # Retrieve output parameters if applicable
        cursor.fetchall()
        # Commit the changes
        connection.commit()
    for i in rev_id:
       # Call the stored procedure
        cursor.callproc('DeleteReview', (i,))
        # Retrieve output parameters if applicable
        cursor.fetchall()
        # Commit the changes
        connection.commit()

    cursor.execute("DELETE FROM User WHERE user_id = %s", (user_id,))
    cursor.fetchall()
    connection.commit()
    
    cursor.close()
    connection.close()
    

def DeleteBook(book_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT reservation_id FROM Reservation WHERE book_id = %s", (book_id,))
    res_id = list()
    while(True):
        x = cursor.fetchone()
        if x is None: break
        res_id.append(x[0])
        
    cursor.execute("SELECT review_id FROM Review WHERE book_id = %s", (book_id,))
    rev_id = list()
    while(True):
        x = cursor.fetchone()
        if x is None: break
        rev_id.append(x[0])
        
    for i in res_id:
       # Call the stored procedure
        cursor.callproc('DeleteReservation', (i,))
        # Retrieve output parameters if applicable
        cursor.fetchall()
        # Commit the changes
        connection.commit()
    for i in rev_id:
       # Call the stored procedure
        cursor.callproc('DeleteReview', (i,))
        # Retrieve output parameters if applicable
        cursor.fetchall()
        # Commit the changes
        connection.commit()
        
    cursor.execute("DELETE FROM Author WHERE book_id = %s", (book_id,))      # delete all authors
    cursor.fetchall()
    connection.commit()
    cursor.execute("DELETE FROM Category WHERE book_id = %s", (book_id,))      # delete all categories
    cursor.fetchall()
    connection.commit()
    cursor.execute("DELETE FROM Keyword WHERE book_id = %s", (book_id,))      # delete all keywords
    cursor.fetchall()
    connection.commit()
    cursor.execute("DELETE FROM Book WHERE book_id = %s", (book_id,))
    cursor.fetchall()
    connection.commit()
    
    cursor.close()
    connection.close()
    
    
def DeleteSchool(school_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT book_id FROM Book WHERE school_id = %s", (school_id,))
    book_id = list()
    while(True):
        x = cursor.fetchone()
        if x is None: break
        book_id.append(x[0])
        
    cursor.execute("SELECT user_id FROM User WHERE school_id = %s", (school_id,))
    user_id = list()
    while(True):
        x = cursor.fetchone()
        if x is None: break
        user_id.append(x[0])
        
    for i in book_id:
       # Call the stored procedure
        cursor.callproc('DeleteBook', (i,))
        # Retrieve output parameters if applicable
        cursor.fetchall()
        # Commit the changes
        connection.commit()
    for i in user_id:
       # Call the stored procedure
        cursor.callproc('DeleteUser', (i,))
        # Retrieve output parameters if applicable
        cursor.fetchall()
        # Commit the changes
        connection.commit()

    cursor.execute("DELETE FROM School WHERE school_id = %s", (school_id,))
    cursor.fetchall()
    connection.commit()
    
    cursor.close()
    connection.close()
    

# --------------------------Login------------------------------ #

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
                return redirect(url_for('admin_home'))

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
    

# ----------------------------User----------------------------------- #

@app.route('/user_homepage')
def user():
    return render_template('home.html')



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
    role = session.get('role')

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


    # Store the new information
    session['username'] = new_username
    session['password'] = new_password
    session['first_name'] = new_first_name
    session['last_name'] = new_last_name

    my_message = "Your info have been updated successfully."

    if role == 'Administrator':
        return render_template(
            'admin_home.html', 
            message = my_message,
            result_1 = session.get('result_1'),
            result_2 = session.get('result_2'),
            result_3 = session.get('result_3'),
            result_4 = session.get('result_4'),
            result_5 = session.get('result_5'),
            result_6 = session.get('result_6'),
            result_7 = session.get('result_7'),
            )
    
    elif role == 'Operator':
        return render_template('operator_homepage.html', message = my_message)
    
    elif role == 'Teacher':
        session['school_name'] = new_school
        query = "SELECT school_id FROM School WHERE school_name = %s"
        params = [new_school]
        cursor.execute(query, params)
        res = cursor.fetchone()
        session['school_id'] = res[0]

    return render_template('home.html', message = my_message)


# --------------------------Operator--------------------------------- #

@app.route('/operator_homepage')
def operator_homepage():
    
    categories = ["Adventure", "Biography", "Children's", "Classics", "Comedy",
    "Crime", "Dystopian", "Fantasy", "Historical Fiction", "Horror"
    "Mystery", "Philosophy", "Poetry", "Romance", "Science Fiction"
    "Self-help", "Short Stories", "Thriller", "Travel", "Young Adult"]
    
    return render_template('operator_homepage.html', categories = categories)



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



@app.route('/operator_books_edit', methods=['POST'])
def edit_books_info():
    update = request.form.get('update')
    delete = request.form.get('delete')
    
    book_id = 0
    if(update is not None):
        book_id = int(update)
        session['book_id'] = book_id
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Book WHERE book_id = %s", (book_id,))
        result = cursor.fetchone()
        session['school_id'] = result[1]
        
        
        return render_template('operator_books_change.html',
            school_id = result[1],
            isbn = result[2],
            title = result[3],
            publisher = result[4],
            number_of_pages = result[5],
            summary = result[6],
            available_copies = result[7],
            img = result[8],
            language = result[9],
            update = int(update),
            books = session.get('books')
            )
    
    elif(delete is not None):
        book_id = int(delete)
        session['book_id'] = book_id
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.callproc('DeleteBook', (book_id,))
        
        column_names = [i[0] for i in cursor.description]
        new_books = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]
        session['books'] = new_books
        
        return render_template('operator_books.html', books = session.get('books'))
        
        

@app.route('/update_book_info', methods=['POST'])
def update_book_info():
    book_id = session.get('book_id')
    school_id = session.get('school_id')
    new_isbn = request.form.get('isbn')
    new_title = request.form.get('title')
    new_publisher = request.form.get('publisher')
    new_number_of_pages = request.form.get('number_of_pages')
    new_summary = request.form.get('summary')
    new_available_copies = request.form.get('available_copies')
    new_img = request.form.get('img')
    new_language = request.form.get('language')


    # Create a new database connection for this request
    connection = get_database_connection()

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    cursor.callproc('UpdateBook',
    (book_id, school_id, new_isbn, new_title, new_publisher, new_number_of_pages, 
     new_summary, new_available_copies, new_img, new_language))
    
    cursor.execute("SELECT * FROM Book WHERE school_id = %s", (school_id,))

    column_names = [i[0] for i in cursor.description]
    new_books = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]
    session['books'] = new_books

    # Commit the changes to the database
    connection.commit()

    # Close the cursor and database connection
    cursor.close()
    connection.close()
    print("Database connection closed")

    my_message = "Your info have been updated successfully."

    return render_template('operator_books.html', message = my_message, books = session.get('books'))



@app.route('/operator_borrowed')
def operator_borrowed():    
    school_id = session.get('school_id')
    
    # Create a new database connection for this request
    connection = get_database_connection()

    # Create a cursor object to interact with the database

    cursor = connection.cursor()
    query = """SELECT b.*, u.first_name, u.last_name, r.loan_date, r.return_date, (r.return_date > NOW()) AS del 
    FROM Reservation AS r JOIN Book AS b ON r.book_id = b.book_id JOIN User AS u ON u.user_id = r.user_id
    WHERE b.school_id = %s AND (r.reservation_status = 'Borrowed' OR r.reservation_status = 'Delayed')"""
    cursor.execute(query, (school_id,))
    column_names = [i[0] for i in cursor.description]
    books = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]
    cursor.close()

    return render_template('operator_borrowed.html', books = books)



@app.route('/operator_borrowed')
def operator_borrowed_return():
    school_id = session.get('school_id')
    book_id = request.form.get('return')
    
    if (book_id is not None):
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.callproc('ReturnBook', (book_id,))
        connection.commit()
        cursor.close()

    return redirect(url_for('operator_borrowed'))



@app.route('/operator_borrowed_user', methods=['POST'])
def operator_borrowed_user():
    school_id = session.get('school_id')
    search = request.form.get('search')
    username = request.form.get('user')
    
    if (search == 'user'):
        connection = get_database_connection()
        cursor = connection.cursor()
        query = """SELECT b.*, u.first_name, u.last_name, r.loan_date, r.return_date,
        (r.return_date > NOW()) AS del FROM Reservation AS r JOIN Book AS b
        ON r.book_id = b.book_id JOIN User AS u ON u.user_id = r.user_id
        WHERE b.school_id = %s AND (r.reservation_status = 'Borrowed'
        OR r.reservation_status = 'Delayed') AND u.username = %s"""
        cursor.execute(query, (school_id,username))
        column_names = [i[0] for i in cursor.description]
        books = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]
        cursor.close()
        
        return render_template('operator_borrowed_user.html', books = books)



@app.route('/operator_reserved')
def operator_reserved():
    school_id = session.get('school_id')
    
    # Create a new database connection for this request
    connection = get_database_connection()

    # Create a cursor object to interact with the database

    cursor = connection.cursor()
    query = """SELECT b.*, u.first_name, u.last_name, r.loan_date, r.return_date
    FROM Reservation AS r JOIN Book AS b ON r.book_id = b.book_id JOIN User AS u 
    ON u.user_id = r.user_id WHERE b.school_id = %s AND r.reservation_status = 'Active'"""
    cursor.execute(query, (school_id,))
    column_names = [i[0] for i in cursor.description]
    books = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]
    cursor.close()

    return render_template('operator_reserved.html', books = books)



@app.route('/operator_users')
def operator_users():
    school_id = session.get('school_id')
    connection = get_database_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM User WHERE approval_status = 'Pending' AND school_id = %s", (school_id,))
    column_names = [i[0] for i in cursor.description]
    pending_users = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]

    cursor.execute("SELECT * FROM User WHERE approval_status = 'Approved' AND school_id = %s", (school_id,))
    column_names = [i[0] for i in cursor.description]
    approved_users = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]

    cursor.execute("SELECT * FROM User WHERE approval_status = 'Rejected' AND school_id = %s", (school_id,))
    column_names = [i[0] for i in cursor.description]
    declined_users = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]

    # Close the cursor and database connection
    cursor.close()
    connection.close()
    print("Database connection closed")


    return render_template('operator_users.html', 
        pending_users = pending_users,
        approved_users = approved_users,
        declined_users = declined_users
    )



@app.route('/operator_users_edit', methods=['POST'])
def operator_users_edit():
    approve = request.form.get('approve')
    decline = request.form.get('decline')
    delete = request.form.get('delete')
    
    user_id = 0
    if(approve is not None):
        user_id = int(approve)
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.callproc('ApproveUser', (user_id,))

        # Commit the changes to the database
        connection.commit()

        # Close the cursor and database connection
        cursor.close()
        connection.close()
        print("Database connection closed")

    elif (decline is not None):
        user_id = int(decline)
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.callproc('RejectUser', (user_id,))
        # Commit the changes to the database
        connection.commit()

        # Close the cursor and database connection
        cursor.close()
        connection.close()
        print("Database connection closed")

    else:
        user_id = int(delete)
        DeleteUser(user_id)
    
    return redirect(url_for('operator_users'))


@app.route('/approval')
def approval():
    role = session.get('role')
    return render_template('approval.html', role = role)



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
    
    query = """SELECT c.category_name, AVG(r.rating) AS review FROM ((Category
    AS c JOIN Book AS b ON b.book_id = c.book_id) JOIN Review AS r ON
    r.book_id = b.book_id) WHERE b.school_id = %s GROUP BY c.category_name ORDER BY c.category_name"""
    params = (school_id,)
    cursor.execute(query, params)
    column_names = [i[0] for i in cursor.description]
    cat_average = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]
    
    query = """SELECT u.first_name, u.last_name, AVG(r.rating) AS review FROM
    ((School AS s JOIN User AS u ON s.school_id = u.school_id) JOIN Review AS r ON
    r.user_id = u.user_id) WHERE u.school_id = %s GROUP BY u.first_name, u.last_name ORDER BY u.last_name"""
    params = (school_id,)
    cursor.execute(query, params)
    column_names = [i[0] for i in cursor.description]
    user_average = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]
    cursor.close()
    
    return render_template('operator_reviews.html',category_average = cat_average, user_average = user_average, pending_users = pending)



@app.route('/operator_reviews', methods=['POST'])
def operator_reviews_new():
    approval = request.form.get('approve')
    decline = request.form.get('decline')
    
    review_id = 0
    if(approval is not None):
        review_id = approval
        query = "UPDATE Review SET approval_status = 'Approved' WHERE review_id = %s"
    else:
        review_id = decline
        query = "UPDATE Review SET approval_status = 'Rejected' WHERE review_id = %s"

    connection = get_database_connection()
    cursor = connection.cursor()
    params = [review_id]
    cursor.execute(query, params)
    connection.commit()
    cursor.close()
    
    return redirect(url_for('operator_reviews'))


# --------------------- Administrator --------------------------- #

# @app.route('/backup_and_restore')
# def backup_restore():
#     operation = request.form.get('submit')
#     if operation == 'backup':
#         return redirect(url_for('backup'))
#     elif operation == 'restore':
#         return redirect(url_for('restore'))
    
    
    
@app.route('/admin_query1', methods=['POST'])
def admin_query1():
    month = request.form.get('month')
    year = request.form.get('year')
    button = request.form.get('search')

    if(button is not None):
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute("""SELECT COUNT(Reservation.reservation_id) AS reservation_count, School.school_name FROM 
	    (Reservation INNER JOIN User ON Reservation.user_id=User.user_id) INNER JOIN School
	    ON School.school_id=User.school_id WHERE (Reservation.reservation_status='Borrowed' OR Reservation.reservation_status='Returned')
        AND MONTH(Reservation.loan_date)=%s AND YEAR(Reservation.loan_date)=%s GROUP BY School.school_name;""", (int(month), int(year)))
        column_names = [i[0] for i in cursor.description]
        query1_info = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]
        cursor.close()
        return '1'



@app.route('/admin_home', methods=['POST'])
def backup_and_return():
    backup = request.form.get('backup')
    restore = request.form.get('restore')

    if (backup == 'backup'):
        # Get the current date and time
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        # Specify the backup file name
        backup_file = f"backup_{timestamp}.sql"

        # MySQL database connection details
        host = 'localhost'
        username = 'root'
        password = 'Stelios.181002'
        database = 'website'

        # Command to create the backup using mysqldump
        backup_command = f"mysqldump -u {username} -p{password} -h {host} {database} > {backup_file}"

        # Execute the backup command
        os.system(backup_command)

        # Redirect to a success page or perform other actions
    return render_template('admin_home.html')



@app.route('/admin_schools')
def admin_schools():
    # Create a new database connection for this request
    connection = get_database_connection()

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM School")

    column_names = [i[0] for i in cursor.description]
    schools = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]
    session['schools'] = schools
    cursor.close()
    
    return render_template('admin_schools.html', schools = schools)



@app.route('/admin_schools_edit', methods=['POST'])
def edit_school_info():
    update = request.form.get('update')
    delete = request.form.get('delete')
    
    school_id = 0
    if(update is not None):
        school_id = int(update)
        session['school_id'] = school_id
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM School WHERE school_id = %s", (school_id,))
        result = cursor.fetchone()
        
        
        return render_template('admin_schools_change.html',
            school_name = result[1],
            address = result[2],
            city = result[3],
            phone = result[4],
            email = result[5],
            director_name = result[6],
            update = int(update),
            schools = session.get('schools')
            )
    
    elif(delete is not None):
        school_id = int(delete)
        session['school_id'] = school_id
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.callproc('DeleteSchool', (school_id,))
        
        column_names = [i[0] for i in cursor.description]
        new_schools = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]
        session['schools'] = new_schools
        
        return render_template('admin_schools.html', schools = session.get('schools'))
        
        

@app.route('/update_school_info', methods=['POST'])
def update_school_info():
    school_id = session.get('school_id')
    new_school_name = request.form.get('school_name')
    new_address = request.form.get('address')
    new_city = request.form.get('city')
    new_phone = request.form.get('phone')
    new_email = request.form.get('email')
    new_director_name = request.form.get('director_name')

    # Create a new database connection for this request
    connection = get_database_connection()

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    cursor.callproc('UpdateSchool',
    (school_id, new_school_name, new_address, new_city, new_phone, new_email, new_director_name))
    
    cursor.execute("SELECT * FROM School")

    column_names = [i[0] for i in cursor.description]
    new_schools = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]
    session['schools'] = new_schools

    # Commit the changes to the database
    connection.commit()

    # Close the cursor and database connection
    cursor.close()
    connection.close()
    print("Database connection closed")


    # # Store the new information
    # session['school_name'] = new_school_name
    # session['address'] = new_address
    # session['city'] = new_city
    # session['phone'] = new_phone
    # session['email'] = new_email
    # session['director_name'] = new_director_name

    my_message = "Your info have been updated successfully."

    return render_template('admin_schools.html', message = my_message, schools = session.get('schools'))



@app.route('/admin_operators')
def admin_operators():
    connection = get_database_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM User WHERE approval_status = 'Pending' AND role = 'Operator'")
    column_names = [i[0] for i in cursor.description]
    pending_operators = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]

    cursor.execute("SELECT * FROM User WHERE approval_status = 'Approved' AND role = 'Operator'")
    column_names = [i[0] for i in cursor.description]
    approved_operators = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]

    cursor.execute("SELECT * FROM User WHERE approval_status = 'Rejected' AND role = 'Operator'")
    column_names = [i[0] for i in cursor.description]
    declined_operators = [dict(zip(column_names, entry)) for entry in cursor.fetchall()]

    # Close the cursor and database connection
    cursor.close()
    connection.close()
    print("Database connection closed")


    return render_template('admin_operators.html', 
        pending_users = pending_operators,
        approved_users = approved_operators,
        declined_users = declined_operators
    )
    
    
    
@app.route('/admin_operators_edit', methods=['POST'])
def admin_operators_edit():
    approve = request.form.get('approve')
    decline = request.form.get('decline')
    delete = request.form.get('delete')
    
    user_id = 0
    if(approve is not None):
        user_id = int(approve)
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.callproc('ApproveUser', (user_id,))

        # Commit the changes to the database
        connection.commit()

        # Close the cursor and database connection
        cursor.close()
        connection.close()
        print("Database connection closed")

    elif (decline is not None):
        user_id = int(decline)
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.callproc('RejectUser', (user_id,))
        # Commit the changes to the database
        connection.commit()

        # Close the cursor and database connection
        cursor.close()
        connection.close()
        print("Database connection closed")

    else:
        user_id = int(delete)
        DeleteUser(user_id)
    
    return redirect(url_for('admin_operators'))


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