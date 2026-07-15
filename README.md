# 23f3001787_TrekkingMapp
MAD 1 IITM Project 

# Trekking Management Application

A role-based web application for adventure organizations to manage trekking activities. Built for the MAD-1 IITM project.

## Roles
- **Admin:** Manages treks, staff, users, and views all bookings.
- **Trek Staff:** Manages assigned treks, participant lists, and updates trek statuses.
- **User (Trekker):** Browses treks, books slots, tracks trekking history, and handles payments.

## Project Structure & Files
- `app.py`: The main Flask application containing all database models, routes, and core business logic.
- `instance/database.db`: The local SQLite database file where all user, trek, and booking data is stored.
- `static/style.css`: Contains all custom styling and brand color variables.
- `templates/base.html`: The master HTML layout containing the navigation bar and global dependencies.
- `templates/index.html`: The homepage featuring the trek search engine and available adventures grid.
- `templates/login.html` & `register.html`: The authentication pages for user login and sign-up.
- `templates/admin_dashboard.html`: The master control panel for admins to create treks and manage users.
- `templates/staff_dashboard.html`: The panel for staff members to manage their assigned treks.
- `templates/trekker_dashboard.html`: The personal user dashboard for viewing booking history.
- `templates/payments.html`: The checkout page for finalizing trek bookings.
- `templates/blacklisted.html`: The suspension page shown to users who have been banned by an admin.

## How to Run the Application

1. **Install Dependencies:**
   python
   ```bash
   pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug
   ```

2. **Run the Application:**
   ```bash
   python app.py
   ```

3. **Access the App:**
   ```
   http://127.0.0.1:9191/
   ```

   you can change this in the last line in app.py

*(Note: The database is pre configured to auto create and generate an initial Admin account upon first run if it does not already exist).*
