CREATE DATABASE IF NOT EXISTS manhwa_db;

USE manhwa_db;

CREATE TABLE IF NOT EXISTS manhwas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    genre VARCHAR(100),
    rating INT,
    status ENUM('Completed', 'Ongoing', 'Want to Read', 'Dropped'),
    image VARCHAR(255)
);