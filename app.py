import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Load DB path from .env
DATABASE = os.getenv('DATABASE_URL').replace("sqlite:///", "")

# Connect to DB
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the DB
def init_db():
    if not os.path.exists(DATABASE):
        with get_db_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
            ''')
            conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            flash('Username already exists. Choose another one.', 'danger')
            return redirect('/register')

        cursor.execute('INSERT INTO users (firstname, lastname, username, email, password) VALUES (?, ?, ?, ?, ?)',
                       (firstname, lastname, username, email, password))
        conn.commit()
        conn.close()
        flash('Registration successful! Please login.', 'success')
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = {
                'id': user[0],
                'firstname': user[1],
                'lastname': user[2],
                'username': user[3]
            }
            return redirect('/profile')
        else:
            flash('Invalid login credentials.', 'danger')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])
    else:
        flash('Please log in to continue.', 'warning')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/login')
    return render_template('profile.html', user=session['user'])


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
