import sqlite3

def create_connection():
    conn = sqlite3.connect('appointments.db')
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            time TEXT,
            doctor TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_appointment(name, date, time, doctor):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO appointments (name, date, time, doctor)
        VALUES (?, ?, ?, ?)
    ''', (name, date, time, doctor))
    conn.commit()
    conn.close()

def fetch_appointments():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM appointments')
    rows = cursor.fetchall()
    conn.close()
    return rows
