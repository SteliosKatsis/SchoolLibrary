DELIMITER //

-- Total Loans per School and Month
CREATE PROCEDURE QLoansPerSchool(IN p_month INT, IN p_year INT)
BEGIN
    SELECT COUNT(Reservation.reservation_id) AS reservation_count, School.school_name FROM 
	(Reservation INNER JOIN User
	ON Reservation.user_id=User.user_id)
	INNER JOIN School
	ON School.school_id=User.school_id
	WHERE (Reservation.reservation_status='Borrowed' OR Reservation.reservation_status='Returned')
    AND MONTH(Reservation.loan_date)=p_month AND YEAR(Reservation.loan_date)=p_year
    GROUP BY School.school_name;
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
    SELECT DISTINCT CONCAT(u.first_name, ' ', u.last_name) AS name FROM
	(((User AS u JOIN School AS s
    ON u.school_id=s.school_id)
    JOIN Book AS b 
    ON s.school_id=b.school_id)
    JOIN Category AS c
    ON c.book_id=b.book_id)
    JOIN Reservation AS r
    ON r.book_id = b.book_id
    WHERE c.category_name=p_category_name
    AND u.role = 'Teacher' AND YEAR(r.loan_date) = YEAR(NOW());
END //


-- Young Teachers With Most Loans
CREATE PROCEDURE QYoungTeacherLoans(IN lim INT)
BEGIN
    SELECT DISTINCT CONCAT(u.first_name, ' ', u.last_name) AS name,
    COUNT(r.reservation_id) AS loan_count
    FROM User AS u JOIN Reservation AS r
    ON u.user_id=r.user_id
	WHERE u.age < 40 AND u.role = 'Teacher'
    GROUP BY CONCAT(u.first_name, ' ', u.last_name)
    ORDER BY COUNT(r.reservation_id) DESC
    LIMIT lim;
END //


-- Authors with no Loans
CREATE PROCEDURE QAuthorsWithNoLoans()
BEGIN
    SELECT DISTINCT a.author_name
    FROM Author AS a
    LEFT JOIN Book AS b ON a.book_id = b.book_id
    LEFT JOIN Reservation AS r ON b.book_id = r.book_id
    GROUP BY a.author_name
    HAVING COUNT(r.reservation_id) = 0;
END //


-- Operators with the same amount of Loans
CREATE PROCEDURE QOperatorSameLoans()
BEGIN
    SELECT CONCAT(u.first_name, ' ', u.last_name) AS name, 
    (SELECT COUNT(reservation_id) AS total_loans
    FROM Reservation as r JOIN Users AS u ON a.book_id = b.book_id
    JOIN School AS s ON s.book_id = u.book_id
    GROUP BY a.author_name
    HAVING COUNT(r.reservation_id) = 0;
END //


-- Authors with books less than 5 from the max
SELECT author_name, COUNT(book_id) AS books
FROM Author GROUP BY author_name
HAVING COUNT(book_id) < ( 
(SELECT COUNT(book_id)
FROM Author GROUP BY author_name
ORDER BY COUNT(book_id) DESC
LIMIT 1) - 5);

DELIMITER ;


DELIMITER //

CREATE PROCEDURE QSchoolsWithSameBookCount()
BEGIN
  SELECT s.school_name, COUNT(*) AS book_count
  FROM School s
  JOIN Book b ON s.school_id = b.school_id
  JOIN Reservation r ON b.book_id = r.book_id
  GROUP BY s.school_id
  HAVING book_count = (
    SELECT COUNT(*)
    FROM School s2
    JOIN Book b2 ON s2.school_id = b2.school_id
    JOIN Reservation r2 ON b2.book_id = r2.book_id
    GROUP BY s2.school_id
    HAVING COUNT(*) = book_count
  );
END //

DELIMITER ;