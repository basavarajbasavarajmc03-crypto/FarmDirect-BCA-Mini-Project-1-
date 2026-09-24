from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
from mysql.connector import Error
from functools import wraps
from datetime import date

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "143142"),
    "database": os.environ.get("DB_NAME", "farmdirect"),
    "port": int(os.environ.get("DB_PORT", "3306"))
}
def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get("role") != role:
                flash("Access denied.", "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route("/")
def index():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT c.*, u.name AS farmer_name
        FROM crops c JOIN users u ON c.farmer_id=u.user_id
        WHERE c.status='Available'
        ORDER BY c.crop_id DESC LIMIT 8
    """)
    crops = cur.fetchall()
    cur.close(); db.close()
    return render_template("index.html", crops=crops)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        phone = request.form["phone"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        role = request.form["role"]
        address = request.form["address"].strip()

        if role not in ("farmer", "buyer"):
            flash("Invalid user type.", "danger")
            return redirect(url_for("register"))

        db = get_db()
        cur = db.cursor()
        try:
            cur.execute("SELECT user_id FROM users WHERE email=%s OR phone=%s", (email, phone))
            if cur.fetchone():
                flash("Email or phone already registered.", "danger")
                return redirect(url_for("register"))
            cur.execute("""
                INSERT INTO users(name,phone,email,password,user_type,address)
                VALUES(%s,%s,%s,%s,%s,%s)
            """, (name, phone, email, generate_password_hash(password), role, address))
            db.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))
        finally:
            cur.close(); db.close()
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]
        db = get_db(); cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close(); db.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["user_id"]
            session["name"] = user["name"]
            session["role"] = user["user_type"]
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    if session["role"] == "farmer":
        return redirect(url_for("farmer_dashboard"))
    if session["role"] == "admin":
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("buyer_dashboard"))

@app.route("/farmer")
@login_required
@role_required("farmer")
def farmer_dashboard():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM crops WHERE farmer_id=%s ORDER BY crop_id DESC", (session["user_id"],))
    crops = cur.fetchall()
    cur.execute("""
        SELECT o.*, c.crop_name, u.name AS buyer_name
        FROM orders o JOIN crops c ON o.crop_id=c.crop_id
        JOIN users u ON o.buyer_id=u.user_id
        WHERE c.farmer_id=%s ORDER BY o.order_id DESC
    """, (session["user_id"],))
    orders = cur.fetchall()
    cur.close(); db.close()
    return render_template("farmer_dashboard.html", crops=crops, orders=orders)

@app.route("/crop/add", methods=["GET","POST"])
@login_required
@role_required("farmer")
def add_crop():
    if request.method == "POST":
        crop_name = request.form["crop_name"].strip()
        quantity = float(request.form["quantity"])
        unit = request.form["unit"]
        price = float(request.form["price"])
        quality = request.form["quality"]
        location = request.form["location"].strip()
        harvest_date = request.form["harvest_date"]

        db = get_db(); cur = db.cursor()
        cur.execute("""
            INSERT INTO crops(farmer_id,crop_name,quantity,unit,price,quality,location,harvest_date,status)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'Available')
        """, (session["user_id"], crop_name, quantity, unit, price, quality, location, harvest_date))
        db.commit(); cur.close(); db.close()
        flash("Crop listed successfully.", "success")
        return redirect(url_for("farmer_dashboard"))
    return render_template("add_crop.html")

@app.route("/crop/delete/<int:crop_id>", methods=["POST"])
@login_required
@role_required("farmer")
def delete_crop(crop_id):
    db = get_db(); cur = db.cursor()
    cur.execute("DELETE FROM crops WHERE crop_id=%s AND farmer_id=%s", (crop_id, session["user_id"]))
    db.commit(); cur.close(); db.close()
    flash("Crop removed.", "success")
    return redirect(url_for("farmer_dashboard"))

@app.route("/buyer")
@login_required
@role_required("buyer")
def buyer_dashboard():
    search = request.args.get("search", "").strip()
    db = get_db(); cur = db.cursor(dictionary=True)
    if search:
        cur.execute("""
            SELECT c.*,u.name AS farmer_name,u.phone AS farmer_phone
            FROM crops c JOIN users u ON c.farmer_id=u.user_id
            WHERE c.status='Available' AND
            (c.crop_name LIKE %s OR c.location LIKE %s)
            ORDER BY c.crop_id DESC
        """, (f"%{search}%", f"%{search}%"))
    else:
        cur.execute("""
            SELECT c.*,u.name AS farmer_name,u.phone AS farmer_phone
            FROM crops c JOIN users u ON c.farmer_id=u.user_id
            WHERE c.status='Available' ORDER BY c.crop_id DESC
        """)
    crops = cur.fetchall()
    cur.execute("""
        SELECT o.*, c.crop_name, u.name AS farmer_name
        FROM orders o JOIN crops c ON o.crop_id=c.crop_id
        JOIN users u ON c.farmer_id=u.user_id
        WHERE o.buyer_id=%s ORDER BY o.order_id DESC
    """, (session["user_id"],))
    orders = cur.fetchall()
    cur.close(); db.close()
    return render_template("buyer_dashboard.html", crops=crops, orders=orders, search=search)

@app.route("/crop/<int:crop_id>")
@login_required
def crop_detail(crop_id):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT c.*,u.name AS farmer_name,u.phone AS farmer_phone,u.email AS farmer_email
        FROM crops c JOIN users u ON c.farmer_id=u.user_id
        WHERE c.crop_id=%s
    """, (crop_id,))
    crop = cur.fetchone()
    cur.close(); db.close()
    if not crop:
        flash("Crop not found.", "danger")
        return redirect(url_for("index"))
    return render_template("crop_detail.html", crop=crop)

@app.route("/order/<int:crop_id>", methods=["POST"])
@login_required
@role_required("buyer")
def place_order(crop_id):
    quantity = float(request.form["quantity"])
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM crops WHERE crop_id=%s AND status='Available'", (crop_id,))
    crop = cur.fetchone()
    if not crop:
        cur.close(); db.close()
        flash("Crop is not available.", "danger")
        return redirect(url_for("buyer_dashboard"))
    if quantity <= 0 or quantity > float(crop["quantity"]):
        cur.close(); db.close()
        flash("Enter a valid quantity.", "danger")
        return redirect(url_for("crop_detail", crop_id=crop_id))
    total = quantity * float(crop["price"])
    cur2 = db.cursor()
    cur2.execute("""
        INSERT INTO orders(buyer_id,crop_id,quantity,total_price,status)
        VALUES(%s,%s,%s,%s,'Pending')
    """, (session["user_id"], crop_id, quantity, total))
    db.commit()
    cur2.close(); cur.close(); db.close()
    flash("Purchase request sent to farmer.", "success")
    return redirect(url_for("buyer_dashboard"))

@app.route("/order/<int:order_id>/<action>", methods=["POST"])
@login_required
@role_required("farmer")
def update_order(order_id, action):
    new_status = {"accept":"Accepted", "reject":"Rejected"}.get(action)
    if not new_status:
        return redirect(url_for("farmer_dashboard"))
    db = get_db(); cur = db.cursor()
    cur.execute("""
        UPDATE orders o JOIN crops c ON o.crop_id=c.crop_id
        SET o.status=%s
        WHERE o.order_id=%s AND c.farmer_id=%s
    """, (new_status, order_id, session["user_id"]))
    db.commit(); cur.close(); db.close()
    flash(f"Order {new_status.lower()}.", "success")
    return redirect(url_for("farmer_dashboard"))

@app.route("/price-suggestion", methods=["GET","POST"])
@login_required
def price_suggestion():
    result = None
    crop_name = ""
    location = ""
    if request.method == "POST":
        crop_name = request.form["crop_name"].strip()
        location = request.form["location"].strip()
        db = get_db(); cur = db.cursor(dictionary=True)
        cur.execute("""
            SELECT AVG(market_price) AS avg_price, MIN(market_price) AS min_price,
                   MAX(market_price) AS max_price, COUNT(*) AS samples
            FROM price_history
            WHERE crop_name=%s AND (%s='' OR location LIKE %s)
        """, (crop_name, location, f"%{location}%"))
        row = cur.fetchone()
        cur.close(); db.close()
        if row and row["avg_price"] is not None:
            avg = float(row["avg_price"])
            result = {
                "average": round(avg,2),
                "suggested_min": round(avg*0.95,2),
                "suggested_max": round(avg*1.05,2),
                "samples": row["samples"]
            }
        else:
            flash("No price history found for this crop/location.", "warning")
    return render_template("price_suggestion.html", result=result, crop_name=crop_name, location=location)

@app.route("/admin")
@login_required
@role_required("admin")
def admin_dashboard():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS n FROM users WHERE user_type='farmer'"); farmers=cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS n FROM users WHERE user_type='buyer'"); buyers=cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS n FROM crops"); crops=cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS n FROM orders"); orders=cur.fetchone()["n"]
    cur.execute("SELECT * FROM price_history ORDER BY price_date DESC, price_id DESC LIMIT 20")
    prices=cur.fetchall()
    cur.close(); db.close()
    return render_template("admin_dashboard.html", farmers=farmers,buyers=buyers,crops=crops,orders=orders,prices=prices)

@app.errorhandler(500)
def server_error(error):
    return render_template("error.html", message="Server/database error. Check your MySQL settings."), 500

if __name__ == "__main__":
    app.run(debug=True)
