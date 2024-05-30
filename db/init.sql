CREATE USER 'wvf_candidates_profile' @'localhost' IDENTIFIED BY 'wvf@sp123&';
CREATE DATABASE IF NOT EXISTS CandidatesProfile;

GRANT ALL PRIVILEGES ON CandidatesProfile.* TO 'wvf_candidates_profile' @'localhost';

FLUSH PRIVILEGES;

USE CandidatesProfile;

CREATE TABLE IF NOT EXISTS Candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender ENUM('male', 'female', 'other') NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100) NOT NULL,
    category ENUM('PWD', 'Non-PWD', 'EWS', 'Women', 'LGBTQ', 'Retired person') NOT NULL,
    disability_type VARCHAR(100) NOT NULL,
    disability_percentage INT(100),
    highest_qualification VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    graduation_year YEAR NOT NULL,
    domain ENUM('IT', 'BFSI', 'MS Office', 'Data Visualization') NOT NULL,
    skills VARCHAR(255) NOT NULL,
    typing_speed VARCHAR(15) NOT NULL,
    quality VARCHAR(15) NOT NULL,
    experience ENUM('0-1 years', '1-3 years', '3-5 years', '5+ years') NOT NULL,
    photo VARCHAR(255) NOT NULL,
    resume VARCHAR(255) NOT NULL,
    video VARCHAR(255) NOT NULL,
    pdf VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    title TEXT NOT NULL,
    date TEXT NOT NULL,
    location TEXT NOT NULL
);
CREATE TABLE event_schedule (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    event_id INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (event_id) REFERENCES events(id)
);
