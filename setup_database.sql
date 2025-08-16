CREATE DATABASE IF NOT EXISTS anpr_system;
USE anpr_system;

CREATE TABLE IF NOT EXISTS authorized_vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plate_number VARCHAR(20) NOT NULL UNIQUE,
    owner_name VARCHAR(100),
    registered_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert some test data
INSERT INTO authorized_vehicles (plate_number, owner_name) VALUES
('ABC123', 'John Doe'),
('XYZ789', 'Jane Smith'); 