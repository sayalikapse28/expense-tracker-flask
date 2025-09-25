# Smart Expense Tracker (Flask)

A Flask-based expense management system with user authentication, expense CRUD, and a Bootstrap UI.

## Features
- Signup, Login, Logout (Flask-Login, Bcrypt)
- Add & Delete Expenses
- Dashboard with expense list
- Category-wise charts using Chart.js
- SQLite database

## Tech Stack
- Python, Flask, SQLAlchemy, Flask-Login
- Bootstrap 5, Chart.js
- SQLite (can be switched to PostgreSQL/MySQL)

## Run Locally
```bash
git clone <your_repo_url>
cd expense_tracker
pip install -r requirements.txt
python app.py
