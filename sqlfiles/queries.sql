DELIMITER //

-- Total Loans per School and Month
CREATE PROCEDURE QLoansPerSchool(IN p_month INT, IN year INT)
BEGIN
    SELECT COUNT(Reservation.reservation_id), School.school_name FROM 
	(Reservation INNER JOIN User
	ON Reservation.user_id=User.user_id)
	INNER JOIN School
	ON School.school_id=User.school_id
	WHERE (reservation_status='Borrowed' OR reservation_status='Returned') AND MONTH(loan_date)=p_month AND YEAR(loan_date)=p_year ;
END //


-- Authors per Category
CREATE PROCEDURE QCategoryAuthor(IN p_category_name VARCHAR(100))
BEGIN
    SELECT DISTINCT a.author_name FROM
	Author AS a JOIN Category AS c
	WHERE a.book_id=c.book_id AND c.category_name=p_category_name;
END //


-- Teacher Loans per Category
CREATE PROCEDURE QCategoryTeachers(IN p_category_name VARCHAR(100))
BEGIN
    SELECT DISTINCT CONCAT(u.first_name, u.last_name) FROM
	(((User AS u JOIN School AS s
    ON u.school_id=s.school_id)
    JOIN Book AS b 
    ON s.school_id=b.school_id)
    JOIN Category AS c
    ON c.book_id=b.book_id)
	WHERE c.category_name=p_category_name;
END //


-- Young Teachers With Most Loans
CREATE PROCEDURE QYoungTeacherLoans(IN lim INT)
BEGIN
    SELECT DISTINCT CONCAT(u.first_name, u.last_name), COUNT(l.loan_id) FROM
	(((User AS u JOIN School AS s
    ON u.school_id=s.school_id)
    JOIN Book AS b 
    ON s.school_id=b.school_id)
    JOIN Loans AS l
    ON l.book_id=b.book_id)
	WHERE u.age<40
    ORDER BY COUNT(l.loan_id) DESC
    LIMIT lim;
END //

DELIMITER ;