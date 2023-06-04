DELIMITER //

-- INSERT SCHOOL

CREATE PROCEDURE InsertSchool(IN p_school_name VARCHAR(100), IN p_address VARCHAR(100), IN p_city VARCHAR(100), IN p_phone VARCHAR(100), IN p_email VARCHAR(100), IN p_director_name VARCHAR(100))
BEGIN
    INSERT INTO School(school_name,address,city,phone,email,director_name)
    VALUES (p_school_name, p_address, p_city, p_phone, p_email, p_director_name);
END //


-- INSERT USER

CREATE PROCEDURE InsertUser(IN p_school_name VARCHAR(100), IN p_username VARCHAR(100), IN p_password VARCHAR(100), IN p_first_name VARCHAR(100), IN p_last_name VARCHAR(100) , IN p_age INT, IN p_role VARCHAR(100))
BEGIN
	DECLARE v_school_id INT;
    DECLARE v_approval_status VARCHAR(15);

    SELECT school_id INTO v_school_id
    FROM School
	WHERE LOWER(REPLACE(school_name, ' ', '')) = LOWER(REPLACE(p_school_name, ' ', '')) COLLATE utf8mb4_general_ci
	LIMIT 1;
    
    IF p_role <> 'Administrator' AND v_school_id IS NULL THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You must insert a valid school';
	END IF;
    
    IF p_role = 'Administrator' THEN
        SET v_school_id = NULL;
        SET v_approval_status = 'Approved';
	ELSE
		SET v_approval_status = 'Pending';
    END IF;
    
    IF ((SELECT COUNT(*) FROM User WHERE role='Administrator')<>0 AND p_role='Administrator') OR
       ((SELECT COUNT(*) FROM User WHERE role='Operator' AND school_id=v_school_id)<>0 AND p_role='Operator') THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You cant sign up with this role';
    ELSE
		INSERT INTO User(school_id,username,password,first_name,last_name,approval_status,age,role)
		VALUES (v_school_id, p_username, p_password, p_first_name, p_last_name, v_approval_status, p_age, p_role);
	END IF;
END //


-- INSERT BOOK

CREATE PROCEDURE InsertBook (
  IN p_school_id INT,
  IN p_book_isbn VARCHAR(13),
  IN p_book_title VARCHAR(200),
  IN p_book_publisher VARCHAR(255),
  IN p_book_num_of_pages INT,
  IN p_book_summary TEXT,
  IN p_book_available_copies INT,
  IN p_book_img TEXT,
  IN p_book_language VARCHAR(5),
  IN p_authors VARCHAR(255),
  IN p_categories VARCHAR(255),
  IN p_keywords VARCHAR(255)
)
BEGIN
  DECLARE book_id INT;

  -- Insert book into Book table
  INSERT INTO Book (school_id, isbn, title, publisher, number_of_pages, summary, available_copies, img, language)
  VALUES (p_school_id, p_book_isbn, p_book_title, p_book_publisher, p_book_num_of_pages, p_book_summary, p_book_available_copies, p_book_img, p_book_language);

  -- Get the auto-generated book_id
  SET book_id = LAST_INSERT_ID();

  -- Insert authors into Author table
  INSERT INTO Author (author_name, book_id)
  SELECT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(p_authors, ',', numbers.n), ',', -1)), book_id
  FROM (
    SELECT 1 + units.i + tens.i * 10 AS n
    FROM (SELECT 0 AS i UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) AS units
    CROSS JOIN (SELECT 0 AS i UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) AS tens
  ) AS numbers
  WHERE numbers.n <= LENGTH(p_authors) - LENGTH(REPLACE(p_authors, ',', '')) + 1;

  -- Insert categories into Category table
  INSERT INTO Category (category_name, book_id)
  SELECT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(p_categories, ',', numbers.n), ',', -1)), book_id
  FROM (
    SELECT 1 + units.i + tens.i * 10 AS n
    FROM (SELECT 0 AS i UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) AS units
    CROSS JOIN (SELECT 0 AS i UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) AS tens
  ) AS numbers
  WHERE numbers.n <= LENGTH(p_categories) - LENGTH(REPLACE(p_categories, ',', '')) + 1;

  -- Insert keywords into Keyword table
  INSERT INTO Keyword (keyword_name, book_id)
  SELECT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(p_keywords, ',', numbers.n), ',', -1)), book_id
  FROM (
    SELECT 1 + units.i + tens.i * 10 AS n
    FROM (SELECT 0 AS i UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) AS units
    CROSS JOIN (SELECT 0 AS i UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) AS tens
  ) AS numbers
  WHERE numbers.n <= LENGTH(p_keywords) - LENGTH(REPLACE(p_keywords, ',', '')) + 1;
END //


-- INSERT REVIEW

CREATE PROCEDURE InsertReview(IN p_user_id INT, IN p_book_id INT, IN p_rating INT, IN p_comment TEXT)
BEGIN
	DECLARE v_school_id INT;
    
    SELECT school_id INTO v_school_id
    FROM User
    WHERE user_id=p_user_id;
    
    IF (SELECT COUNT(*) FROM Book WHERE book_id=p_book_id AND school_id=v_school_id)<>0 THEN
		INSERT INTO Review(user_id,book_id,rating,comment)
		VALUES (p_user_id, p_book_id, p_rating, p_comment);
	END IF;
END //


-- INSERT RESERVATION

CREATE PROCEDURE InsertReservation(IN p_user_id INT, IN p_book_id INT, IN p_loan_date TIMESTAMP, IN p_return_date TIMESTAMP)
BEGIN
	DECLARE v_school_id INT;
	DECLARE v_reserved_books INT;
    DECLARE v_borrowed_books INT;
	DECLARE v_available_copies INT;
    DECLARE v_role VARCHAR(15);

	-- Get the school ID of the user
	SELECT school_id INTO v_school_id
	FROM User
	WHERE user_id = p_user_id;
    
    -- Get the role of the user
    SELECT role INTO v_role
	FROM User
	WHERE user_id = p_user_id;
    
    -- Check if the user has delayed any books    
	IF (SELECT COUNT(*) FROM Reservation WHERE user_id = p_user_id AND reservation_status='Delayed') > 0 THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You have delayed books in your posession.';
	END IF;
    
    -- Check if the user has an active reservation on the book trying to borrow
	IF (SELECT COUNT(*) FROM Reservation WHERE user_id = p_user_id AND reservation_status = 'Borrowed' AND book_id = p_book_id) > 0 THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You have the same book in your posession.';
	END IF;

	-- Check if the user has already reserved books in the current week
	SELECT COUNT(*) INTO v_reserved_books
	FROM Reservation
	WHERE user_id = p_user_id AND (reservation_status = 'Active' OR reservation_status = 'Pending')
		AND WEEK(reservation_date) = WEEK(NOW()) AND YEAR(reservation_date) = YEAR(NOW());
        
	-- Check if the user has already borrowed books in the current week
	SELECT COUNT(*) INTO v_borrowed_books
	FROM Reservation
	WHERE user_id = p_user_id AND reservation_status = 'Borrowed'
		AND WEEK(reservation_date) = WEEK(NOW()) AND YEAR(reservation_date) = YEAR(NOW());
    
	IF (v_reserved_books >= 2 OR v_borrowed_books >=2) AND v_role = 'Student' THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You have already reserved two books this week.';
    ELSEIF (v_reserved_books >= 1 OR v_borrowed_books >=1) AND v_role = 'Teacher' THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You have already reserved one book this week.';
	ELSEIF v_role = 'Operator' OR v_role = 'Administrator' THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You cannot reserve a book.';
	END IF;

	-- Check if there are available copies of the book
	SELECT available_copies INTO v_available_copies
	FROM Book
	WHERE book_id = p_book_id AND school_id = v_school_id;

	IF v_available_copies > 0 THEN
		-- Insert the reservation
		INSERT INTO Reservation (user_id, book_id, reservation_date, loan_date, return_date, reservation_status)
		VALUES (p_user_id, p_book_id, NOW(), p_loan_date, p_return_date, 'Active');

		UPDATE Book
		SET available_copies=v_available_copies-1
		WHERE book_id=p_book_id;
   
	ELSE
		-- Insert the reservation in Pending mode
		INSERT INTO Reservation (user_id, book_id, reservation_date, loan_date, return_date, reservation_status)
		VALUES (p_user_id, p_book_id, NOW(), p_loan_date, p_return_date, 'Pending');
	END IF;
END//


-- CREATE EVENT

CREATE EVENT IF NOT EXISTS reservation_update
ON SCHEDULE EVERY 1 HOUR
DO
BEGIN
    -- Update the reservations with 'Pending' status to 'Expired' if the retrieval date is in the past
    UPDATE Reservation
    SET reservation_status = 'Canceled'
    WHERE reservation_status = 'Pending' AND NOW() > DATE_ADD(reservation_date, INTERVAL 7 DAY);
    
    UPDATE Reservation
    SET reservation_status = 'Delayed'
    WHERE reservation_status = 'Borrowed' AND NOW() > return_date;
END //

DELIMITER ;