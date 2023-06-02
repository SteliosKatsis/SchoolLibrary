DELIMITER //

-- UPDATE SCHOOL

CREATE PROCEDURE UpdateSchool(IN p_school_id INT, IN p_school_name VARCHAR(100), IN p_address VARCHAR(100), IN p_city VARCHAR(100), IN p_phone VARCHAR(100), IN p_email VARCHAR(100), IN p_director_name VARCHAR(100))
BEGIN
	UPDATE School
    SET school_name=p_school_name, address=p_address, city=p_city, phone=p_phone, email=p_email, director_name=p_director_name
    WHERE school_id=p_school_id;
END //


-- UPDATE BOOK

CREATE PROCEDURE UpdateBook(IN p_book_id INT, IN p_school_id INT, IN p_isbn VARCHAR(13), IN p_title VARCHAR(200), IN p_publisher VARCHAR(255), IN p_number_of_pages INT, IN p_summary TEXT, IN p_available_copies INT, IN p_img BLOB, IN p_language VARCHAR(5))
BEGIN
	UPDATE Book
    SET isbn=p_isbn, title=p_title, publisher=p_publisher, number_of_pages=p_number_of_pages, summary=p_summary, available_copies=p_available_copies, img=p_img, language=p_language
    WHERE book_id=p_book_id;
END //


-- UPDATE USER

CREATE PROCEDURE UpdateUser(IN p_user_id INT, IN p_school_name VARCHAR(100), IN p_username VARCHAR(100), IN p_password VARCHAR(100), IN p_first_name VARCHAR(100), IN p_last_name VARCHAR(100))
BEGIN
	DECLARE v_school_id INT;

	SELECT school_id INTO v_school_id
    FROM School
	WHERE LOWER(REPLACE(school_name, ' ', '')) = LOWER(REPLACE(p_school_name, ' ', '')) COLLATE utf8mb4_general_ci
	LIMIT 1;
	
	UPDATE USER
    SET school_id=v_school_id, username=p_username, password=p_password, first_name=p_first_name, last_name=p_last_name
    WHERE user_id=p_user_id;
END //


-- APPROVE USER

CREATE PROCEDURE ApproveUser(IN p_user_id INT)
BEGIN
	UPDATE USER
    SET approval_status = 'Approved'
    WHERE user_id = p_user_id;
END //


-- REJECT USER

CREATE PROCEDURE RejectUser(IN p_user_id INT)
BEGIN
	UPDATE USER
    SET approval_status = 'Rejected'
    WHERE user_id = p_user_id;
END //


-- UPDATE RESERVATION

CREATE PROCEDURE UpdateReservation(IN p_reservation_id INT)
BEGIN
	DECLARE v_book_id INT;
	DECLARE v_pending_users INT;
    
	SELECT book_id INTO v_book_id
    FROM Reservation
    WHERE reservation_id=p_reservation_id;
    
    SELECT COUNT(*) INTO v_pending_users
    FROM Reservation
    WHERE reservation_status = 'Pending' AND book_id = v_book_id;
    
    IF v_pending_users > 0 THEN
		SELECT reservation_id INTO @v_next_in_queue
		FROM Reservation
		WHERE reservation_status = 'Pending' AND book_id = v_book_id
		ORDER BY reservation_date ASC
		LIMIT 1;
        
		UPDATE Reservation
        SET reservation_status = 'Active'
        WHERE reservation_id = @v_next_in_queue;
	ELSE
		SELECT available_copies INTO @v_available_copies
        FROM Book
        WHERE book_id=v_book_id;
        
		UPDATE Books
        SET available_copies = @v_available_copies + 1
        WHERE book_id=v_book_id;
	END IF;
END //


-- CANCEL RESERVATION

CREATE PROCEDURE CancelReservation(IN p_reservation_id INT)
BEGIN
	CALL UpdateReservation(p_reservation_id);
    
    UPDATE Reservation
    SET reservation_status = 'Canceled'
    WHERE reservation_id = p_reservation_id;
END //


-- RETURN BOOK

CREATE PROCEDURE ReturnBook(IN p_reservation_id INT)
BEGIN
	CALL UpdateReservation(p_reservation_id);
    
	UPDATE Reservation
    SET reservation_status = 'Returned'
    WHERE reservation_id = p_reservation_id;
END //

DELIMITER ;