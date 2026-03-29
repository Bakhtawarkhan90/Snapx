from flask import Flask, request, redirect, url_for, send_from_directory
import mysql.connector
import os
import time

app = Flask(__name__, static_url_path='/static', static_folder='.')

# 🔁 Connect to MySQL with retry
while True:
    try:
        db = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "database"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "kali"),
            database=os.getenv("MYSQL_DATABASE", "table")
        )
        print("✅ Database connected")
        break
    except mysql.connector.Error as err:
        print(f"❌ Database connection failed: {err}")
        time.sleep(5)

# 🧱 Create contact table
cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS contact_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    subject VARCHAR(200),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
cursor.close()

# 🏠 Serve HTML
@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

# 📥 Handle form submit
@app.route('/Send Message Now', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    subject = request.form.get('subject')
    message = request.form.get('message')

    try:
        cursor = db.cursor()
        query = """
        INSERT INTO contact_messages (name, email, phone, subject, message)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (name, email, phone, subject, message)

        cursor.execute(query, values)
        db.commit()
        cursor.close()

        print("✅ Message saved:", values)

    except mysql.connector.Error as err:
        print(f"❌ Insert error: {err}")

    return redirect(url_for('thank_you'))

# ✅ Thank you page
@app.route('/thank_you')
def thank_you():
    return "<h2>✅ Message Sent Successfully!</h2>"

# 📂 Static files
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.getcwd(), filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
