
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3, secrets, os, datetime

DB = 'tennis.db'

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, surname TEXT, email TEXT UNIQUE, password TEXT,
            age INTEGER, address TEXT, failed_attempts INTEGER DEFAULT 0,
            locked INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            court TEXT,
            date TEXT,
            time TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

mensaje = "Hola desde mi rama lucero"


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'devsecretkey')

@app.before_first_request
def setup():
    init_db()

def get_db_conn():
    return sqlite3.connect(DB)

@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        surname = request.form.get('surname','').strip()
        email = request.form.get('email','').strip().lower()
        age = int(request.form.get('age','0'))
        address = request.form.get('address','').strip()
        if age < 18:
            flash('Debe ser mayor de 18 años para registrarse.', 'error')
            return render_template('register.html')
        password = secrets.token_urlsafe(8)
        conn = get_db_conn()
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (name,surname,email,password,age,address) VALUES (?,?,?,?,?,?)',
                      (name,surname,email,password,age,address))
            conn.commit()
        except Exception as e:
            conn.close()
            flash('Error: email ya registrado.', 'error')
            return render_template('register.html')
        conn.close()
        # For demo we show the generated password on the confirmation page.
        return render_template('registered.html', email=email, password=password)
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','').strip()
        conn = get_db_conn()
        c = conn.cursor()
        c.execute('SELECT id,password,failed_attempts,locked FROM users WHERE email=?', (email,))
        row = c.fetchone()
        if not row:
            flash('Usuario no encontrado.', 'error')
            conn.close()
            return render_template('login.html')
        user_id, real_pw, failed_attempts, locked = row
        if locked:
            flash('Cuenta bloqueada. Contacte al administrador.', 'error')
            conn.close()
            return render_template('login.html')
        if password == real_pw:
            c.execute('UPDATE users SET failed_attempts=0 WHERE id=?', (user_id,))
            conn.commit()
            conn.close()
            session['user_id'] = user_id
            return redirect(url_for('courts'))
        else:
            failed_attempts += 1
            if failed_attempts >= 3:
                c.execute('UPDATE users SET failed_attempts=?, locked=1 WHERE id=?', (failed_attempts, user_id))
                flash('Cuenta bloqueada tras 3 intentos fallidos.', 'error')
            else:
                c.execute('UPDATE users SET failed_attempts=? WHERE id=?', (failed_attempts, user_id))
                flash(f'Credenciales incorrectas. Intentos fallidos: {failed_attempts}', 'error')
            conn.commit()
            conn.close()
            return render_template('login.html')
    return render_template('login.html')

@app.route('/courts', methods=['GET','POST'])
def courts():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    courts = ['Cancha 1', 'Cancha 2', 'Cancha 3']
    message = None
    if request.method == 'POST':
        court = request.form.get('court')
        date = request.form.get('date')
        time = request.form.get('time')
        try:
            selected = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            if (selected - datetime.date.today()).days < 2:
                message = 'No se puede reservar con menos de 2 días de anticipación.'
            else:
                # check for occupation (simple check)
                conn = get_db_conn()
                c = conn.cursor()
                c.execute('SELECT id FROM bookings WHERE court=? AND date=? AND time=?', (court,date,time))
                if c.fetchone():
                    message = 'Cancha ocupada, por favor seleccione otro día y horario.'
                else:
                    c.execute('INSERT INTO bookings (user_id,court,date,time,created_at) VALUES (?,?,?,?,?)',
                              (session['user_id'], court, date, time, datetime.datetime.now().isoformat()))
                    conn.commit()
                    message = 'Su turno ha sido registrado con éxito.'
                conn.close()
        except Exception as e:
            message = 'Formato de fecha inválido.'
    return render_template('courts.html', courts=courts, message=message)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
