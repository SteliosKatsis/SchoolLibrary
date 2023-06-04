DELIMITER //

-- DELETE RESERVATION

CREATE PROCEDURE DeleteReservation(IN p_reservation_id INT)
BEGIN
	DECLARE v_role VARCHAR(50);

	SELECT reservation_status INTO v_role
    FROM Reservation
    WHERE reservation_id = p_reservation_id;
    
    IF v_role = 'Pending' OR v_role = 'Returned' THEN
		DELETE FROM Reservation WHERE reservation_id = p_reservation_id;
	ELSEIF v_role = 'Active' THEN
		CALL CancelReservation(p_reservation_id);
        
        DELETE FROM Reservation WHERE reservation_id = p_reservation_id;
	ELSE
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A user still possesses a book.';

    END IF;
END //


-- DELETE REVIEW

CREATE PROCEDURE DeleteReview(IN p_review_id INT)
BEGIN
	DELETE FROM Review WHERE review_id=p_review_id;
END //


-- DELETE BOOK (with deleting associated reservations and reviews)

CREATE PROCEDURE DeleteBook(IN p_book_id INT)
BEGIN
	-- Declare variables
	DECLARE review_id INT;
	DECLARE reservation_id INT;
	DECLARE done INT DEFAULT FALSE;

	-- Declare cursor for reviews and reservations
	DECLARE cur_reviews CURSOR FOR SELECT review_id FROM review WHERE book_id = p_book_id;
	DECLARE cur_reservations CURSOR FOR SELECT reservation_id FROM reservation WHERE book_id = p_book_id;

	-- Declare continue handler
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

	-- Delete reviews
	OPEN cur_reviews;
	read_loop: LOOP
		FETCH cur_reviews INTO review_id;
		IF done THEN
			LEAVE read_loop;
		END IF;

		-- Call DeleteReview procedure
		CALL DeleteReview(review_id);
	END LOOP;

	CLOSE cur_reviews;
  
	SET done = FALSE;

	-- Delete reservations
	OPEN cur_reservations;
	read_loop2: LOOP
		FETCH cur_reservations INTO reservation_id;
		IF done THEN
			LEAVE read_loop2;
		END IF;
	
		-- Call DeleteReservation procedure
		CALL DeleteReservation(reservation_id);
	END LOOP;

	CLOSE cur_reservations;

	-- Delete any dependencies
	DELETE FROM Author WHERE book_id = p_book_id;
    DELETE FROM Category WHERE book_id = p_book_id;
    DELETE FROM Keyword WHERE book_id = p_book_id;

	-- Delete the user
	DELETE FROM Book WHERE book_id = p_book_id;
END //


-- DELETE USER (with deleting associated reservations and reviews)

CREATE PROCEDURE DeleteUser(IN p_user_id INT)
BEGIN
	-- Declare variables
	DECLARE review_id INT;
	DECLARE reservation_id INT;
	DECLARE done INT DEFAULT FALSE;

	-- Declare cursor for reviews and reservations
	DECLARE cur_reviews CURSOR FOR SELECT review_id FROM review WHERE user_id = p_user_id;
	DECLARE cur_reservations CURSOR FOR SELECT reservation_id FROM reservation WHERE user_id = p_user_id;

	-- Declare continue handler
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

	-- Delete reviews
	OPEN cur_reviews;
	read_loop: LOOP
		FETCH cur_reviews INTO review_id;
		IF done THEN
			LEAVE read_loop;
		END IF;

		-- Call DeleteReview procedure
		CALL DeleteReview(review_id);
	END LOOP;

	CLOSE cur_reviews;
  
	SET done = FALSE;

	-- Delete reservations
	OPEN cur_reservations;
	read_loop2: LOOP
		FETCH cur_reservations INTO reservation_id;
		IF done THEN
			LEAVE read_loop2;
		END IF;

    -- Call DeleteReservation procedure
		CALL DeleteReservation(reservation_id);
	END LOOP;

	CLOSE cur_reservations;

	-- Delete the user
	DELETE FROM User WHERE user_id = p_user_id;
END //


-- DELETE SCHOOL (with deleting associated users and books)

CREATE PROCEDURE DeleteSchool(IN p_school_id INT)
BEGIN
	-- Declare variables
	DECLARE user_id INT;
	DECLARE book_id INT;
	DECLARE done INT DEFAULT FALSE;

	-- Declare cursor for users and books
	DECLARE cur_users CURSOR FOR SELECT user_id FROM User WHERE school_id = p_school_id;
	DECLARE cur_books CURSOR FOR SELECT book_id FROM Book WHERE school_id = p_school_id;

	-- Declare continue handler
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

	-- Delete users
	OPEN cur_users;
	read_loop: LOOP
		FETCH cur_users INTO user_id;
		IF done THEN
			LEAVE read_loop;
		END IF;

		-- Call DeleteUser procedure
		CALL DeleteUser(user_id);
	END LOOP;

	CLOSE cur_users;
  
	SET done = FALSE;

	-- Delete books
	OPEN cur_books;
	read_loop2: LOOP
		FETCH cur_books INTO book_id;
		IF done THEN
			LEAVE read_loop2;
		END IF;

		-- Call DeleteBook procedure
		CALL DeleteBook(book_id);
	END LOOP;

	CLOSE cur_books;

	-- Delete the school
	DELETE FROM School WHERE school_id = p_school_id;
END //

DELIMITER ;