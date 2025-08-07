import os
import sqlite3
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from tools_engine import run_tool
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
                    firstname TEXT NOT NULL,
                    lastname TEXT NOT NULL,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    plan TEXT DEFAULT 'Free Tier',
                    last_login TEXT,
                    tools_used INTEGER DEFAULT 0
                )
            ''')
            conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tools/<tool_name>', methods=['GET', 'POST'])
def tool(tool_name):
    if 'user' not in session:
        flash('Please log in to access tools.', 'warning')
        return redirect('/login')

    output = None
    description_map = {
        "ai-writer": "Generate professional content using AI for blogs, emails, or documents.",
        "code-assistant": "Get code snippets, debugging help, or quick functions from AI.",
        "design-helper": "Design support using AI for wireframes or mockups.",
        "legal-advisor": "Generate legal templates, contracts, or get quick AI legal info.",
        "health-bot": "Ask health-related questions powered by AI (not medical advice)."
    }

    if request.method == 'POST':
        user_input = request.form.get('inputData', '').strip()

        if user_input:
            output = run_tool(tool_name, user_input)
            flash("Tool launched successfully!", "success")

            # Update tools_used count
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET tools_used = tools_used + 1 WHERE id = ?', 
                (session['user']['id'],))
            conn.commit()
            conn.close()
        else:
            flash("Please provide some input.", "warning")

    return render_template(
        'tool_template.html',
        tool_name=tool_name.replace('-', ' ').title(),
        tool_description=description_map.get(tool_name, "Use AI to boost productivity."),
        output=output,
        user=session['user']
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            flash('Username already exists. Choose another one.', 'danger')
            return redirect('/register')

        cursor.execute('''
            INSERT INTO users (firstname, lastname, username, email, password)
            VALUES (?, ?, ?, ?, ?)
        ''', (firstname, lastname, username, email, password))
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

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()

        if user:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (now, user['id']))
            conn.commit()

            session['user'] = {
                'id': user['id'],
                'firstname': user['firstname'],
                'lastname': user['lastname'],
                'username': user['username'],
                'email': user['email']
            }

            conn.close()
            return redirect('/profile')
        else:
            conn.close()
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

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT firstname, lastname, email, plan, last_login, tools_used 
        FROM users WHERE id = ?
    ''', (session['user']['id'],))
    user_data = cursor.fetchone()
    conn.close()

    if not user_data:
        flash('User not found.', 'danger')
        return redirect('/logout')

    user_profile = {
        'name': f"{user_data['firstname']} {user_data['lastname']}",
        'email': user_data['email'],
        'plan': user_data['plan'],
        'last_login': user_data['last_login'],
        'tools_used': user_data['tools_used']
    }

    return render_template('profile.html', user=session['user'], profile=user_profile)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

