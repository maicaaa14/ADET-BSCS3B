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
            cursor.execute(insert_query, (first_name, middle_name, last_name, address, email, contact_number, password))  # Changed variable name here
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
        email = request.form['email']  
        password = encrypt_password(request.form['password'])  

        conn = get_db_connection()
        if conn is None:
            return "Database connection failed", 500

        cursor = conn.cursor()
        cursor.execute('SELECT id, first_name FROM adet_user WHERE email = %s AND password = %s', (email, password))  
        user = cursor.fetchone()

        if user:
            session['loggedin'] = True
            session['id'] = user[0]
            session['first_name'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your credentials.', 'error')

        cursor.close()
        conn.close()

    return render_template('login.html')

# Dashboard route 
@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT first_name, middle_name, last_name, address, email, contact_number FROM adet_user WHERE id = %s', (session['id'],))  
        user_details = cursor.fetchone()

        return render_template('dashboard.html', first_name=session['first_name'], user_details=user_details)
    else:
        return redirect(url_for('login'))

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
