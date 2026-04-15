CREATE DATABASE IF NOT EXISTS minicloud;
USE minicloud;
CREATE TABLE IF NOT EXISTS notes(
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO notes(title) VALUES ('Hello from MariaDB!');

CREATE DATABASE IF NOT EXISTS studentdb;
USE studentdb;

CREATE TABLE IF NOT EXISTS students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(10) NOT NULL,
    fullname VARCHAR(100) NOT NULL,
    dob DATE,
    major VARCHAR(50)
);

INSERT INTO students (student_id, fullname, dob, major) VALUES 
('52300020', 'Phan Nhut Duy', '2005-01-25', 'Software Engineering'),
('52300021', 'Vo Dat Hai', '2003-01-01', 'Software Engineering'),
('52100001', 'Nguyen Van A', '2003-01-15', 'Software Engineering'),
('52100002', 'Tran Thi B', '2003-05-20', 'Data Science'),
('52100003', 'Le Van C', '2002-11-30', 'Information Assurance');