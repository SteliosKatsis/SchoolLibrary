CREATE DATABASE website;

USE website;

CREATE TABLE School (
  school_id INT AUTO_INCREMENT,
  school_name VARCHAR(100) NOT NULL,
  address VARCHAR(100) NOT NULL,
  city VARCHAR(100) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  email VARCHAR(100) NOT NULL,
  director_name VARCHAR(100) NOT NULL,
  PRIMARY KEY (school_id, school_name)
);

CREATE TABLE User (
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  school_id INT,
  username VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(100) UNIQUE NOT NULL,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  approval_status VARCHAR(20) DEFAULT 'Pending' CHECK (approval_status IN ('Approved', 'Pending', 'Rejected')) NOT NULL,
  age INT CHECK (Age BETWEEN 6 AND 65) NOT NULL,
  role VARCHAR(20) CHECK (role IN ('Student', 'Teacher', 'Operator', 'Administrator')) NOT NULL,
  FOREIGN KEY (school_id) REFERENCES School (school_id)
);

CREATE TABLE Book (
  book_id INT PRIMARY KEY AUTO_INCREMENT,
  school_id INT NOT NULL,
  isbn VARCHAR(100) NOT NULL,
  title VARCHAR(200) NOT NULL,
  publisher VARCHAR(100),
  number_of_pages INT,
  summary TEXT,
  available_copies INT NOT NULL,
  img BLOB,
  language VARCHAR(5) NOT NULL,
  FOREIGN KEY (school_id) REFERENCES School (school_id)
);

CREATE TABLE Author (
  author_name VARCHAR(50) NOT NULL,
  book_id INT  NOT NULL,
  PRIMARY KEY (author_name, book_id),
  FOREIGN KEY (book_id) REFERENCES Book (book_id)
);

CREATE TABLE Category (
  category_name VARCHAR(50) NOT NULL,
  book_id INT  NOT NULL,
  PRIMARY KEY (category_name, book_id),
  FOREIGN KEY (book_id) REFERENCES Book (book_id)
);

CREATE TABLE Keyword (
  keyword_name VARCHAR(50) NOT NULL,
  book_id INT NOT NULL,
  PRIMARY KEY (keyword_name, book_id),
  FOREIGN KEY (book_id) REFERENCES Book (book_id)
);

CREATE TABLE Reservation (
  reservation_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  book_id INT NOT NULL,
  reservation_date TIMESTAMP NOT NULL,
  loan_date TIMESTAMP NOT NULL,
  return_date TIMESTAMP NOT NULL,
  reservation_status VARCHAR(20) CHECK (reservation_status IN ('Active', 'Pending', 'Borrowed', 'Returned', 'Delayed', 'Canceled')) NOT NULL,
  FOREIGN KEY (user_id) REFERENCES User (user_id),
  FOREIGN KEY (book_id) REFERENCES Book (book_id),
  CHECK (DATEDIFF(loan_date,reservation_date) BETWEEN 0 AND 7),
  CHECK (DATEDIFF(return_date,loan_date) BETWEEN 0 AND 60)
);

CREATE TABLE Review (
  review_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  book_id INT NOT NULL,
  rating INT CHECK (Rating BETWEEN 1 AND 5) NOT NULL,
  comment TEXT,
  approval_status VARCHAR(20) DEFAULT 'Pending' CHECK (approval_status IN ('Approved', 'Pending', 'Rejected')) NOT NULL,
  FOREIGN KEY (user_id) REFERENCES User (user_id),
  FOREIGN KEY (book_id) REFERENCES Book (book_id)
);

DROP DATABASE website;
