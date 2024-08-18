from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'Sheli@123'
DATABASE = 'database.db'

def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY,
                      username TEXT,
                      password TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS skills (
                      id INTEGER PRIMARY KEY,
                      username TEXT,
                      skill_title TEXT UPPER UNIQUE NOT NULL,
                      progress INTEGER) ''')
    conn.commit()
    conn.close()

def insert_user(username, password):
    conn = sqlite3.connect(DATABASE)  # Fixed: '=' was used instead of '='
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username.upper(), password))
    conn.commit()
    conn.close()

def get_user(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username.upper(), password))
    user = cursor.fetchone()
    conn.close()
    return user

def delete_skill(username, skill_title):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM skills WHERE username=? AND UPPER(skill_title)=?", (username, skill_title.upper()))
    conn.commit()
    conn.close()

create_table()

@app.route('/')
def home():
    if 'username' not in session: 
        return redirect(url_for('login'))
    else:
        return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Password and Confirm Password do not match')
        
        else:
            insert_user(username, password)
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username, password)
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password') 
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/api/get_info')
def get_info():
    data = {'info': 'some data'}
    return jsonify(data)

@app.route('/skills')
def skills():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Connect to the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Retrieve skills for the current user
    username = session['username']
    cursor.execute("SELECT * FROM skills WHERE username=?", (username,))
    skills = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Render the skills template and pass the skills to it
    return render_template('skills.html', skills=skills)



def insert_skill(username, skill_title, progress):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM skills WHERE username=? AND UPPER(skill_title)=?", (username, skill_title.lower()))
    existing_skill = cursor.fetchone()
    if existing_skill:
        conn.close()
        return "Skill already exists" 

    cursor.execute("INSERT INTO skills (username, skill_title, progress) VALUES (?,?,?)",(username, skill_title, progress))
    conn.commit()
    conn.close()
    flash('Skill added successfully!')


@app.route('/add_skill', methods=["POST"])
def add_skill():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        skill_title = request.form['skill_title']
        progress = request.form['progress']
        username = session['username']
        insert_skill(username, skill_title, progress)
        return redirect(url_for('skills'))

@app.route('/delete_skill/<skill_title>', methods=["GET", "POST"])
def delete_skill_route(skill_title):
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = session['username']
        delete_skill(username, skill_title)
        flash('Skill deleted successfully!')
        return redirect(url_for('skills'))
    return "This route only accepts POST requests."

@app.route('/search', methods=['POST'])
def search():
    username = request.form.get('username')
    if not username:
        flash('Please enter a username to search')
        return render_template('home.html')

    # Convert the entered username to lowercase for case-insensitive search
    username = username.lower()

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Use the lower() function in the SQL query to make the comparison case-insensitive
    cursor.execute("SELECT * FROM skills WHERE LOWER(username)=?", (username,))
    skills = cursor.fetchall()
    conn.close()

    if not skills:
        flash("User not found!")
        return render_template('home.html')

    return render_template('search_results.html', username=username, skills=skills)


@app.route('/trigger_alert', methods=['GET'])
def trigger_alert():
    alert_message = 'This is an alert message!'
    return jsonify({'message': alert_message})

if __name__ == '__main__':
    app.run(debug=True)
