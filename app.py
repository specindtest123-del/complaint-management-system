from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from database.db import init_db, get_db_connection
from model.sentiment_model import analyzer
from datetime import datetime
import sqlite3
import functools

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize database
init_db()

# Login required decorator
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin', False):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                       (username, password)).fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['is_admin'] = user['is_admin']
        return jsonify({'success': True, 'is_admin': user['is_admin']})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)',
                    (username, email, password, 0))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Username or email already exists'})

@app.route('/api/complaints', methods=['POST'])
@login_required
def submit_complaint():
    data = request.json
    title = data.get('title')
    description = data.get('description')
    category = data.get('category')
    
    # Analyze sentiment
    sentiment, sentiment_score = analyzer.analyze_sentiment(description)
    
    # Predict priority
    priority = analyzer.predict_priority(title, description)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO complaints (user_id, title, description, category, sentiment, 
                               sentiment_score, priority, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (session['user_id'], title, description, category, sentiment, 
          sentiment_score, priority, 'Pending'))
    
    complaint_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True, 
        'complaint_id': complaint_id,
        'sentiment': sentiment,
        'priority': priority
    })

@app.route('/api/user/complaints')
@login_required
def get_user_complaints():
    conn = get_db_connection()
    complaints = conn.execute('''
        SELECT * FROM complaints 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return jsonify([dict(c) for c in complaints])

@app.route('/api/admin/complaints')
@admin_required
def get_all_complaints():
    conn = get_db_connection()
    complaints = conn.execute('''
        SELECT c.*, u.username 
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        ORDER BY 
            CASE priority 
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
            END,
            created_at DESC
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(c) for c in complaints])

@app.route('/api/admin/complaint/<int:complaint_id>', methods=['PUT'])
@admin_required
def update_complaint(complaint_id):
    data = request.json
    status = data.get('status')
    assigned_to = data.get('assigned_to')
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE complaints 
        SET status = ?, assigned_to = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, assigned_to, complaint_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/logout')
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/track')
@login_required
def track_complaints():
    return render_template('user_track.html')

if __name__ == '__main__':
    app.run(debug=True)