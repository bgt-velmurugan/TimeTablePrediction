import sqlite3
import json

def init_db():
    conn = sqlite3.connect('timetables.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS timetables
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  department TEXT UNIQUE,
                  data TEXT)''')
    conn.commit()
    conn.close()

def save_timetable(department, timetable, timetable_id=None):
    conn = sqlite3.connect('timetables.db')
    c = conn.cursor()
    if timetable_id:
        c.execute("UPDATE timetables SET data = ? WHERE id = ?", (json.dumps(timetable), timetable_id))
    else:
        c.execute("INSERT INTO timetables (department, data) VALUES (?, ?)", (department, json.dumps(timetable)))
        timetable_id = c.lastrowid
    conn.commit()
    conn.close()
    return timetable_id

def load_timetable(timetable_id):
    conn = sqlite3.connect('timetables.db')
    c = conn.cursor()
    c.execute("SELECT department, data FROM timetables WHERE id = ?", (timetable_id,))
    result = c.fetchone()
    conn.close()
    if result:
        return {"department": result[0], "data": result[1]}
    return None

def get_all_timetables():
    conn = sqlite3.connect('timetables.db')
    c = conn.cursor()
    c.execute("SELECT id, department FROM timetables")
    result = c.fetchall()
    conn.close()
    return result

def update_timetable(timetable_id, timetable):
    conn = sqlite3.connect('timetables.db')
    c = conn.cursor()
    c.execute("UPDATE timetables SET data = ? WHERE id = ?", (json.dumps(timetable), timetable_id))
    conn.commit()
    conn.close()

def delete_timetable(timetable_id):
    conn = sqlite3.connect('timetables.db')
    c = conn.cursor()
    c.execute("DELETE FROM timetables WHERE id = ?", (timetable_id,))
    conn.commit()
    conn.close()

def timetable_exists(department):
    conn = sqlite3.connect('timetables.db')
    c = conn.cursor()
    c.execute("SELECT id FROM timetables WHERE department = ?", (department,))
    result = c.fetchone()
    conn.close()
    return result is not None

