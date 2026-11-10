# Examlytics — Online Examination & Big Data Analytics

A database-driven online examination system with a modern dashboard and student performance analytics.

## Features
- Student registration and CSV import
- Subject-wise multiple-choice question bank
- Online examination and automatic evaluation
- Results stored in SQLite database
- Performance dashboard: score distribution, subject averages, pass rate
- Filter, export and download examination results
- Downloadable database backup

## Technology
- Python + Streamlit
- SQLite relational database
- Pandas for data processing
- Plotly for interactive analytics

## Run locally
1. Install Python 3.10 or later.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment (recommended).
4. Install dependencies:

   `pip install -r requirements.txt`

5. Start the application:

   `streamlit run app.py`

6. Open the local URL shown in the terminal (usually http://localhost:8501).

The database `online_exam.db` is created automatically on first run and seeded with demo students and questions.

## CSV format for student import
Use these exact column names:

`roll_no,name,department,year`

Example:
`DS006,Meena Kumar,Data Science,III`

## Project modules
1. Dashboard
2. Take Examination
3. Question Bank
4. Students
5. Results & Analytics
6. Database Tools

## Academic note
This is a ready-to-run academic prototype. For production use, add authentication, role-based access, password hashing, exam timers, audit logs, and secure deployment.
