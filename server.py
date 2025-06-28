from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime

# Load environment variables from .env
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY')

# Load data at the start
try:
    ml = pd.ExcelFile('ML Portal.xlsx')
    ds = pd.ExcelFile('DS PORTAL.xlsx')
    da = pd.ExcelFile('DA PORTAL.xlsx')

    # Personal Information DataFrames
    personal_info_df_ml = ml.parse('PERSONAL INFORMATION', dtype={'Phone Number': str})
    personal_info_df_ds = ds.parse('PERSONAL INFORMATION', dtype={'Phone Number': str})
    personal_info_df_da = da.parse('PERSONAL INFORMATION', dtype={'Phone Number': str})

    # Attendance DataFrames
    att_df_ml = ml.parse('ATTENDANCE')
    att_df_ds = ds.parse('ATTENDANCE')
    att_df_da = da.parse('ATTENDANCE')

    # Overall Performance DataFrames
    ass_df_ml = ml.parse('OVERALL PERFORMANCE')
    ass_df_ds = ds.parse('OVERALL PERFORMANCE')
    ass_df_da = da.parse('OVERALL PERFORMANCE')

    # Project Progress DataFrames (fixed variable names)
    project_progress_ml = ml.parse('OVERALL PERFORMANCE')
    project_progress_ds = ds.parse('OVERALL PERFORMANCE')
    project_progress_da = da.parse('OVERALL PERFORMANCE')
    
    print("Excel files loaded successfully")
    
except Exception as e:
    print(f"Error loading Excel files: {e}")
    # Initialize empty DataFrames if files can't be loaded
    personal_info_df_ml = pd.DataFrame()
    personal_info_df_ds = pd.DataFrame()
    personal_info_df_da = pd.DataFrame()
    att_df_ml = pd.DataFrame()
    att_df_ds = pd.DataFrame()
    att_df_da = pd.DataFrame()
    ass_df_ml = pd.DataFrame()
    ass_df_ds = pd.DataFrame()
    ass_df_da = pd.DataFrame()
    project_progress_ml = pd.DataFrame()
    project_progress_ds = pd.DataFrame()
    project_progress_da = pd.DataFrame()

def format_date(date_value):
    """Helper function to format dates and remove time"""
    if date_value == 'N/A' or pd.isna(date_value) or str(date_value).strip() == '':
        return 'N/A'
    
    try:
        date_str = str(date_value)
        
        # Handle different date formats
        if 'T' in date_str or '+' in date_str:
            # ISO format: 2024-12-15T00:00:00+00:00 or 2025-03-15 00:00:00+00:00
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        elif ' ' in date_str and ':' in date_str:
            # Format: 2025-03-15 00:00:00
            date_obj = datetime.strptime(date_str.split(' ')[0], "%Y-%m-%d")
        else:
            # Simple format: 2024-12-15
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Return formatted date without time
        return date_obj.strftime("%B %d, %Y")
    
    except Exception as e:
        # If parsing fails, try to extract just the date part
        try:
            date_part = str(date_value).split(' ')[0]
            if len(date_part) >= 10:  # Basic date format check
                return date_part
        except:
            pass
        return str(date_value)

def get_value(df, match_col, match_val, target_col):
    """Helper function to get a value from a DataFrame"""
    if df.empty or match_col not in df.columns or target_col not in df.columns:
        return 'N/A'
    
    df_copy = df.copy()
    df_copy[match_col] = df_copy[match_col].astype(str).str.strip().str.lower()
    row = df_copy[df_copy[match_col] == match_val.lower()]
    return row.iloc[0][target_col] if not row.empty else 'N/A'

def calculate_attendance(att_df, email):
    """Calculate attendance statistics for a student"""
    if att_df.empty:
        return "No record", 0, 0
    
    att_df_copy = att_df.copy()
    att_df_copy['Email'] = att_df_copy['Email'].astype(str).str.strip().str.lower()
    att_row = att_df_copy[att_df_copy['Email'] == email]

    if not att_row.empty:
        attendance_cols = [
            col for col in att_df.columns if col not in ['Email', 'Name']
        ]
        present = 0
        total = 0

        for col in attendance_cols:
            status = str(att_row.iloc[0].get(col, '')).strip().upper()
            if status == 'P/N':
                present += 1
                total += 1
            elif status == 'A/N':
                total += 1

        return f"{present}/{total} sessions", present, total - present
    else:
        return "No record", 0, 0

@app.route('/')
def index():
    return render_template('index.html', details=None)

@app.route('/learning')
def learning_page():
    return render_template('learning.html')

@app.route('/learning.html')
def learning_html():
    return render_template('learning.html')

@app.route('/setting')
def setting_page():
    return render_template('setting.html')

@app.route('/setting.html')
def setting_html():
    return render_template('setting.html')

@app.route('/validation')
def validation_page():
    return render_template('validation.html')

@app.route('/validation.html')
def validation_html():
    return render_template('validation.html')

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'phone' not in data:
            return jsonify({
                "success": False,
                "message": "Email and phone are required"
            }), 400
            
        email = data['email'].strip().lower()
        phone = str(data['phone']).strip()

        # Check if any DataFrames are empty
        if personal_info_df_ml.empty and personal_info_df_ds.empty and personal_info_df_da.empty:
            return jsonify({
                "success": False,
                "message": "Data not available. Please contact administrator."
            }), 500

        # Normalize DataFrame columns for all three datasets
        datasets = [
            (personal_info_df_ml, att_df_ml, ass_df_ml, project_progress_ml, 'ML'),
            (personal_info_df_ds, att_df_ds, ass_df_ds, project_progress_ds, 'DS'),
            (personal_info_df_da, att_df_da, ass_df_da, project_progress_da, 'DA')
        ]
        
        user_found = False
        user_data = None
        dataset_type = None
        
        for personal_df, att_df, ass_df, proj_df, ds_type in datasets:
            if not personal_df.empty:
                personal_df_copy = personal_df.copy()
                personal_df_copy['Email'] = personal_df_copy['Email'].astype(str).str.strip().str.lower()
                personal_df_copy['Phone Number'] = personal_df_copy['Phone Number'].astype(str).str.strip()
                
                user_row = personal_df_copy[(personal_df_copy['Email'] == email) & 
                                          (personal_df_copy['Phone Number'] == phone)]
                
                if not user_row.empty:
                    user_found = True
                    user_data = (personal_df, att_df, ass_df, proj_df)
                    dataset_type = ds_type
                    break
        
        if not user_found:
            return jsonify({
                "success": False,
                "message": "Invalid credentials"
            }), 401
        
        # Extract data based on found dataset
        personal_df, att_df, ass_df, proj_df = user_data
        
        # Get basic information (initialize all variables with defaults)
        name = get_value(personal_df, 'Email', email, 'Name')
        domain = get_value(personal_df, 'Email', email, 'Domain')
        time = get_value(personal_df, 'Email', email, 'Session Timings')
        mode = get_value(personal_df, 'Email', email, 'Mode')
        
        # Get optional fields (may not exist in all datasets) - ensure all are initialized
        college = get_value(personal_df, 'Email', email, 'COLLEGE')
        dept = get_value(personal_df, 'Email', email, 'DEPT')
        trainer = get_value(personal_df, 'Email', email, 'TRAINER')
        days = get_value(personal_df, 'Email', email, 'Days')  # This will return 'N/A' if not found
        
        # Get dates
        registration_date = format_date(get_value(personal_df, 'Email', email, 'Registration date'))
        start_date = format_date(get_value(personal_df, 'Email', email, 'Session start Date'))
        end_date = format_date(get_value(personal_df, 'Email', email, 'Session end date'))
        
        # Get assessment data
        project_title = get_value(ass_df, 'Email', email, 'Project title')
        assessment1 = get_value(ass_df, 'Email', email, 'Assesment 1')
        assessment2 = get_value(ass_df, 'Email', email, 'Assesment 2')
        task = get_value(ass_df, 'Email', email, 'Task')
        project_mark = get_value(ass_df, 'Email', email, 'Project marks')
        final_validation = get_value(ass_df, 'Email', email, 'Final validation')
        total_mark = get_value(ass_df, 'Email', email, 'Total')
        
        # Get attendance data
        per = get_value(att_df, 'Email', email, 'ATTENDNACE')
        stipend_eligibility = get_value(att_df, 'Email', email, 'STIPEND')
        stipend_reason = get_value(att_df, 'Email', email, 'REASON')
        
        # Calculate detailed attendance if possible
        attendance_summary, present, missed = calculate_attendance(att_df, email)

        # Store user details in session
        session['details'] = {
            'name': str(name),
            'email': email,
            'phone': phone,
            'time': str(time),
            'days': str(days),
            'domain': str(domain),
            'college': str(college),
            'dept': str(dept),
            'trainer': str(trainer),
            'mode': str(mode),
            'project_title': str(project_title),
            'registration_date': str(registration_date),
            'start_date': str(start_date),
            'end_date': str(end_date),
            'assessment1': str(assessment1),
            'assessment2': str(assessment2),
            'task': str(task),
            'project_mark': str(project_mark),
            'final_validation': str(final_validation),
            'total_mark': str(total_mark),
            'stipend_eligibility': str(stipend_eligibility),
            'stipend_reason': str(stipend_reason),
            'present': present,
            'missed': missed,
            'per': str(per),
            'attendance_summary': attendance_summary,
            'dataset_type': dataset_type
        }

        return jsonify({"success": True, "redirect": "/details"})

    except Exception as e:
        print(f"Login error: {str(e)}")  # Log the error
        return jsonify({
            "success": False,
            "message": f"An error occurred during login. Please try again."
        }), 500

@app.route('/details')
def details():
    if 'details' not in session:
        return redirect(url_for('index'))
    return render_template('details.html', details=session['details'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)