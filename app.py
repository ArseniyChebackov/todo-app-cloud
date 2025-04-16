import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'dev'  # Change for production!

def get_db_connection():
    db_host = os.getenv('DB_HOST', 'localhost')  # Default to localhost for Windows
    
    # Windows/Linux detection
    is_windows = sys.platform.startswith('win')
    
    if db_host.startswith('/cloudsql/') and not is_windows:
        # Cloud SQL Proxy connection (Linux/Cloud)
        return pymysql.connect(
            unix_socket=db_host,
            user='root',
            password='',
            database='todo_app',
            cursorclass=pymysql.cursors.DictCursor
        )
    else:
        # Standard TCP connection (Windows/Local)
        return pymysql.connect(
            host=db_host,
            user='root',
            password='',
            database='todo_app',
            cursorclass=pymysql.cursors.DictCursor
        )

# Initialize table only if not exists
try:
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
        conn.commit()
except Exception as e:
    print(f"Database initialization error: {e}")


# Initialize database table
with get_db_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    conn.commit()

@app.route('/')
def index():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            tasks = cursor.fetchall()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form['title']
    description = request.form['description']
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tasks (title, description) VALUES (%s, %s)",
                (title, description)
            )
        conn.commit()
    flash('Task added!', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE tasks SET title=%s, description=%s WHERE id=%s",
                    (title, description, task_id)
                )
            conn.commit()
        flash('Task updated!', 'success')
        return redirect(url_for('index'))
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task = cursor.fetchone()
    return render_template('edit.html', task=task)

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
    flash('Task deleted!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)