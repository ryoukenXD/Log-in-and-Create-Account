CREATE DATABASE personnel_db;
USE personnel_db;

-- Personnel Table (Basic Info)
CREATE TABLE personnel (
    personnel_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    birthdate DATE,
    birth_place VARCHAR(255),
    present_address TEXT,
    provincial_address TEXT,
    marital_status ENUM('Single', 'Married') NOT NULL,
    spouse_name VARCHAR(255) NULL
);

-- Positions Table (Job Positions)
CREATE TABLE positions (
    position_id INT AUTO_INCREMENT PRIMARY KEY,
    position_name VARCHAR(255) UNIQUE NOT NULL
);

-- Employment Details Table (Current Employment Status)
CREATE TABLE employment_details (
    employment_id INT AUTO_INCREMENT PRIMARY KEY,
    personnel_id INT NOT NULL,
    position_id INT,
    status ENUM('Contractual', 'Regular') NOT NULL,
    date_hired DATE,
    latest_evaluation DATE,
    basic_salary DECIMAL(10,2),
    FOREIGN KEY (personnel_id) REFERENCES personnel(personnel_id) ON DELETE CASCADE,
    FOREIGN KEY (position_id) REFERENCES positions(position_id) ON DELETE SET NULL
);

-- Dependents Table (Children or Dependents)
CREATE TABLE dependents (
    dependent_id INT AUTO_INCREMENT PRIMARY KEY,
    personnel_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    FOREIGN KEY (personnel_id) REFERENCES personnel(personnel_id) ON DELETE CASCADE
);

-- Parents Table (Mother & Father Information)
CREATE TABLE parents (
    parent_id INT AUTO_INCREMENT PRIMARY KEY,
    personnel_id INT NOT NULL,
    parent_type ENUM('Mother', 'Father') NOT NULL,
    name VARCHAR(255) NOT NULL,
    occupation VARCHAR(255) NULL,
    contact_number VARCHAR(20) NULL,
    FOREIGN KEY (personnel_id) REFERENCES personnel(personnel_id) ON DELETE CASCADE
);

-- Educational Background Table
CREATE TABLE education (
    education_id INT AUTO_INCREMENT PRIMARY KEY,
    personnel_id INT NOT NULL,
    level ENUM('Elementary', 'High School', 'College', 'Other') NOT NULL,
    school_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (personnel_id) REFERENCES personnel(personnel_id) ON DELETE CASCADE
);

-- Employment Record Table (Past Job Records)
CREATE TABLE employment_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    personnel_id INT NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    address TEXT,
    start_year YEAR NOT NULL,
    end_year YEAR NULL,
    contact_number VARCHAR(20),
    FOREIGN KEY (personnel_id) REFERENCES personnel(personnel_id) ON DELETE CASCADE
);

-- Important Identifications Table
CREATE TABLE identifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personnel_id INT NOT NULL,
    sss VARCHAR(20),
    philhealth VARCHAR(20),
    pag_ibig VARCHAR(20),
    tin VARCHAR(20),
    FOREIGN KEY (personnel_id) REFERENCES personnel(personnel_id) ON DELETE CASCADE
)

DESCRIBE personnel;
