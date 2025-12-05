
# Tennis Court Booking - Demo Project

Simple web app (Flask + SQLite) for handling registration, login and court booking.
This project was generated to match the requirements in a course exercise:
- Registration with name, surname, email (username), age (>=18) and address.
- System generates a password on registration (displayed for demo).
- Login with lockout after 3 failed attempts.
- Welcome page showing courts and basic booking form (bookings must be >= 2 days from today).

## Run locally
1. Create a virtualenv and install requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   flask run
   ```
3. Open http://127.0.0.1:5000/register
