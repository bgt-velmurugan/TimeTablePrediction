from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from timetable_generator import generate_timetable, adjust_timetable
from database import init_db, save_timetable, load_timetable, get_all_timetables, update_timetable, delete_timetable, timetable_exists
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a real secret key
init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        department = request.form['department']
        classes_per_day = int(request.form['classes_per_day'])
        days_per_week = int(request.form['days_per_week'])
        staff_subjects = [tuple(pair.split(':')) for pair in request.form['staff_subjects'].split(',')]

        if timetable_exists(department):
            flash(f"A timetable for {department} already exists. Please choose a different name.", "error")
            return redirect(url_for('index'))

        timetable, staff_summary = generate_timetable(department, classes_per_day, days_per_week, staff_subjects)
        timetable_data = {
            'timetable': timetable,
            'staff_summary': staff_summary
        }
        timetable_id = save_timetable(department, timetable_data)
        return redirect(url_for('view_timetable', timetable_id=timetable_id))

    return render_template('index.html')

@app.route('/timetable/<int:timetable_id>')
def view_timetable(timetable_id):
    timetable_data = load_timetable(timetable_id)
    if timetable_data:
        data = json.loads(timetable_data['data'])
        return render_template('timetable.html', 
                               timetable=data['timetable'], 
                               staff_summary=data['staff_summary'], 
                               department=timetable_data['department'], 
                               timetable_id=timetable_id)
    return "Timetable not found", 404

@app.route('/adjust_timetable/<int:timetable_id>', methods=['POST'])
def adjust_timetable_route(timetable_id):
    timetable = load_timetable(timetable_id)
    if timetable:
        data = request.json
        adjusted_timetable = adjust_timetable(json.loads(timetable['data']), data['day'], data['oldIndex'], data['newIndex'])
        save_timetable(timetable['department'], adjusted_timetable, timetable_id)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Timetable not found"}), 404

@app.route('/list_timetables')
def list_timetables():
    timetables = get_all_timetables()
    return render_template('list_timetables.html', timetables=timetables)

@app.route('/edit_timetable/<int:timetable_id>', methods=['GET', 'POST'])
def edit_timetable(timetable_id):
    timetable_data = load_timetable(timetable_id)
    if not timetable_data:
        return "Timetable not found", 404

    if request.method == 'POST':
        updated_timetable = json.loads(request.form['timetable'])
        update_timetable(timetable_id, updated_timetable)
        return redirect(url_for('view_timetable', timetable_id=timetable_id))
    
    data = json.loads(timetable_data['data'])
    return render_template('edit_timetable.html', 
                           timetable=data['timetable'], 
                           department=timetable_data['department'], 
                           timetable_id=timetable_id)

@app.route('/delete_timetable/<int:timetable_id>', methods=['POST'])
def delete_timetable_route(timetable_id):
    delete_timetable(timetable_id)
    flash("Timetable deleted successfully", "success")
    return redirect(url_for('list_timetables'))

if __name__ == '__main__':
    app.run(debug=True)

