from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import date, datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database setup
def get_db_connection():
    conn = sqlite3.connect('hrm.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Create tables
    conn.execute('''CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    department_id INTEGER,
                    hire_date TEXT,
                    position TEXT,
                    salary REAL,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (department_id) REFERENCES departments(id))''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER,
                    date TEXT,
                    status TEXT,
                    check_in_time TEXT,
                    check_out_time TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees(id))''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS leaves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER,
                    start_date TEXT,
                    end_date TEXT,
                    reason TEXT,
                    leave_type TEXT,
                    status TEXT DEFAULT 'Pending',
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees(id))''')
    
    # Insert sample data if tables are empty
    if conn.execute('SELECT COUNT(*) FROM departments').fetchone()[0] == 0:
        sample_departments = ['Human Resources', 'Engineering', 'Marketing', 'Finance', 'Operations']
        for dept in sample_departments:
            conn.execute('INSERT INTO departments (name) VALUES (?)', (dept,))
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Routes
@app.route('/')
def dashboard():
    conn = get_db_connection()
    
    # Get dashboard statistics
    total_employees = conn.execute('SELECT COUNT(*) FROM employees').fetchone()[0]
    total_departments = conn.execute('SELECT COUNT(*) FROM departments').fetchone()[0]
    present_today = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'Present'", 
        (date.today().strftime('%Y-%m-%d'),)
    ).fetchone()[0]
    pending_leaves = conn.execute(
        "SELECT COUNT(*) FROM leaves WHERE status = 'Pending'"
    ).fetchone()[0]
    
    conn.close()
    
    return render_template('index.html', 
                         total_employees=total_employees,
                         total_departments=total_departments,
                         present_today=present_today,
                         pending_leaves=pending_leaves)

# API Routes
@app.route('/api/departments', methods=['GET', 'POST'])
def departments_api():
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.get_json()
        try:
            conn.execute('INSERT INTO departments (name) VALUES (?)', (data['name'],))
            conn.commit()
            return jsonify({'success': True, 'message': 'Department added successfully'})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': 'Department already exists'})
        finally:
            conn.close()
    
    departments = conn.execute('SELECT * FROM departments ORDER BY name').fetchall()
    conn.close()
    return jsonify([dict(row) for row in departments])

@app.route('/api/employees', methods=['GET', 'POST'])
def employees_api():
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.get_json()
        try:
            conn.execute('''INSERT INTO employees 
                           (name, email, department_id, hire_date, position, salary, phone) 
                           VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (data['name'], data['email'], data['department_id'], 
                         data['hire_date'], data['position'], data['salary'], data['phone']))
            conn.commit()
            return jsonify({'success': True, 'message': 'Employee added successfully'})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': 'Email already exists'})
        finally:
            conn.close()
    
    employees = conn.execute('''SELECT e.*, d.name as department_name 
                               FROM employees e 
                               LEFT JOIN departments d ON e.department_id = d.id 
                               ORDER BY e.name''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in employees])

@app.route('/api/attendance', methods=['GET', 'POST'])
def attendance_api():
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.get_json()
        # Check if attendance already exists for this employee and date
        existing = conn.execute('''SELECT id FROM attendance 
                                  WHERE employee_id = ? AND date = ?''',
                               (data['employee_id'], data['date'])).fetchone()
        
        if existing:
            conn.execute('''UPDATE attendance 
                           SET status = ?, check_in_time = ?, check_out_time = ?
                           WHERE id = ?''',
                        (data['status'], data.get('check_in_time'), 
                         data.get('check_out_time'), existing[0]))
        else:
            conn.execute('''INSERT INTO attendance 
                           (employee_id, date, status, check_in_time, check_out_time) 
                           VALUES (?, ?, ?, ?, ?)''',
                        (data['employee_id'], data['date'], data['status'],
                         data.get('check_in_time'), data.get('check_out_time')))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Attendance recorded successfully'})
    
    attendance = conn.execute('''SELECT a.*, e.name as employee_name 
                                FROM attendance a 
                                JOIN employees e ON a.employee_id = e.id 
                                ORDER BY a.date DESC, e.name''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in attendance])

@app.route('/api/leaves', methods=['GET', 'POST'])
def leaves_api():
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.get_json()
        conn.execute('''INSERT INTO leaves 
                       (employee_id, start_date, end_date, reason, leave_type) 
                       VALUES (?, ?, ?, ?, ?)''',
                    (data['employee_id'], data['start_date'], data['end_date'],
                     data['reason'], data['leave_type']))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Leave request submitted successfully'})
    
    leaves = conn.execute('''SELECT l.*, e.name as employee_name 
                            FROM leaves l 
                            JOIN employees e ON l.employee_id = e.id 
                            ORDER BY l.applied_at DESC''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in leaves])

@app.route('/api/leaves/<int:leave_id>/approve', methods=['POST'])
def approve_leave(leave_id):
    conn = get_db_connection()
    conn.execute('UPDATE leaves SET status = "Approved" WHERE id = ?', (leave_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Leave approved successfully'})

@app.route('/api/leaves/<int:leave_id>/reject', methods=['POST'])
def reject_leave(leave_id):
    conn = get_db_connection()
    conn.execute('UPDATE leaves SET status = "Rejected" WHERE id = ?', (leave_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Leave rejected successfully'})

if __name__ == '__main__':
    app.run(debug=True)