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

DELIMITER ;