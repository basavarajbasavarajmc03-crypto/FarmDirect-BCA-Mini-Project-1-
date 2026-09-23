# FarmDirect - BCA Mini Project

FarmDirect connects farmers directly with buyers and provides a simple crop-price suggestion feature.

## Features
- Farmer registration/login
- Buyer registration/login
- Admin dashboard
- Farmer crop listing
- Crop search
- Direct purchase requests
- Farmer order accept/reject
- Price suggestion from stored market-price history
- MySQL database
- Responsive Bootstrap UI

## 1. Install Python
Install Python 3.10+.

## 2. Install MySQL
Install MySQL Server and MySQL Workbench.

## 3. Create database
Open MySQL Workbench and run `schema.sql`.

## 4. Configure database
Open `app.py` and change:
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",
    "database": "farmdirect"
}

## 5. Install packages
Open terminal in this project folder:
python -m venv venv

Windows:
venv\Scripts\activate

Then:
pip install -r requirements.txt

## 6. Run
python app.py

Open:
http://127.0.0.1:5000

## Create admin
Use this Python command after installing Werkzeug:
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('Admin@123'))"

Copy the output and run:
INSERT INTO users(name,phone,email,password,user_type,address)
VALUES('Administrator','9999999999','admin@farmdirect.com','PASTE_HASH_HERE','admin','Bengaluru');

Admin login:
Email: admin@farmdirect.com
Password: Admin@123

Change the password for real use.

## Suggested BCA project modules
1. User Management
2. Farmer Management
3. Buyer Management
4. Crop Management
5. Price Suggestion
6. Order Management
7. Admin Management
8. Database Management
