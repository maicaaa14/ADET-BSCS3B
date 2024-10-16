from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'adet'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def encrypt_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def home():
    return redirect(url_for('registration'))

# Registration route
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        first_name = request.form['first-name']
        middle_name = request.form['middle-name']
        last_name = request.form['last-name']
        address = request.form['address']
        email = request.form['email']  
        contact_number = request.form['contact-number']
        password = encrypt_password(request.form['password'])  

        conn = get_db_connection()
        if conn is None:
            return "Database connection failed", 500

        cursor = conn.cursor()

        try:
            insert_query = '''
                INSERT INTO adet_user (first_name, middle_name, last_name, address, email, contact_number, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (first_name, middle_name, last_name, address, email, contact_number, password))
            conn.commit()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as e:
            print(f"Error inserting data: {e}")
            return "Error inserting data into the database", 500
        finally:
            cursor.close()
            conn.close()

    return render_template('registration.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = hashlib.sha256(request.form.get('password').encode()).hexdigest()

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM adet_user WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                session['email'] = email  
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials. Please try again.", "error")
                return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

# Dashboard route 
@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))

    user_email = session['email']
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT first_name, middle_name, last_name, contact_number, email, address FROM adet_user WHERE email = %s", (user_email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        return f"Error: {err}"

    return render_template('dashboard.html', user=user)

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
