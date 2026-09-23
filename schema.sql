CREATE DATABASE IF NOT EXISTS farmdirect;
USE farmdirect;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    user_type ENUM('farmer','buyer','admin') NOT NULL,
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS crops (
    crop_id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    crop_name VARCHAR(100) NOT NULL,
    quantity DECIMAL(12,2) NOT NULL,
    unit VARCHAR(20) NOT NULL DEFAULT 'kg',
    price DECIMAL(12,2) NOT NULL,
    quality VARCHAR(50),
    location VARCHAR(150),
    harvest_date DATE,
    status ENUM('Available','Sold','Unavailable') DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT NOT NULL,
    crop_id INT NOT NULL,
    quantity DECIMAL(12,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    status ENUM('Pending','Accepted','Rejected','Completed','Cancelled') DEFAULT 'Pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES crops(crop_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS price_history (
    price_id INT AUTO_INCREMENT PRIMARY KEY,
    crop_name VARCHAR(100) NOT NULL,
    market_price DECIMAL(12,2) NOT NULL,
    location VARCHAR(150),
    price_date DATE NOT NULL
);

INSERT INTO price_history(crop_name,market_price,location,price_date) VALUES
('Tomato',24,'Bengaluru','2026-09-20'),
('Tomato',25,'Bengaluru','2026-09-21'),
('Tomato',26,'Bengaluru','2026-09-22'),
('Onion',28,'Bengaluru','2026-09-20'),
('Onion',30,'Bengaluru','2026-09-21'),
('Onion',29,'Bengaluru','2026-09-22'),
('Potato',22,'Bengaluru','2026-09-20'),
('Potato',24,'Bengaluru','2026-09-21'),
('Potato',23,'Bengaluru','2026-09-22');

-- Create admin after installation:
-- Generate a password hash using Python and insert it.
