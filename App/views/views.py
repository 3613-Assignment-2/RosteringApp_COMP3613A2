from flask import Blueprint, request, jsonify
from App.models.staff import Staff
from App.models.shift import Shift
from App.models.timeentry import TimeEntry
from App.controllers.controllers import (
    login, schedule_shift, view_roster, time_in, time_out, view_shift_report, change_password
)

views = Blueprint('views', __name__)

@views.route('/view_roster', methods=['POST'])
def view_roster_route():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = login(username, password)
    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401

    roster = view_roster(user)
    return jsonify({'roster': roster}), 200

@views.route('/schedule', methods=['POST'])
def schedule_shift_route():
    data = request.json
    admin_username = data.get('admin_username')
    admin_password = data.get('admin_password')
    staff_username = data.get('staff_username')
    date = data.get('date')
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    admin = login(admin_username, admin_password)
    staff = Staff.query.filter_by(username=staff_username).first()
    if not admin or not staff:
        return jsonify({'error': 'Admin login failed or staff not found'}), 401

    shift = schedule_shift(admin, staff, date, start_time, end_time)
    if shift:
        return jsonify({
            'message': 'Shift scheduled',
            'staff': staff.username,
            'date': shift.date.isoformat(),
            'start': shift.start_time.isoformat(),
            'end': shift.end_time.isoformat()
        }), 200
    return jsonify({'error': 'Shift could not be scheduled'}), 400

@views.route('/time_in', methods=['POST'])
def time_in_route():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    shift_id = data.get('shift_id')

    user = login(username, password)
    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401

    entry = time_in(user, shift_id)
    if entry:
        return jsonify({'time_in': entry.time_in.isoformat()}), 200
    return jsonify({'error': 'Time in failed'}), 400

@views.route('/time_out', methods=['POST'])
def time_out_route():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    shift_id = data.get('shift_id')

    user = login(username, password)
    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401

    entry = time_out(user, shift_id)
    if entry:
        return jsonify({'time_out': entry.time_out.isoformat()}), 200
    return jsonify({'error': 'Time out failed'}), 400

@views.route('/view_report', methods=['POST'])
def view_report_route():
    data = request.json
    admin_username = data.get('admin_username')
    admin_password = data.get('admin_password')

    admin = login(admin_username, admin_password)
    if not admin or admin.role != 'Admin':
        return jsonify({'error': 'Only Admins can view reports'}), 401

    report = view_shift_report(admin)
    return jsonify({'report': report}), 200

@views.route('/change_password', methods=['POST'])
def change_password_route():
    data = request.json
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    success = change_password(username, old_password, new_password)
    if success:
        return jsonify({'message': 'Password updated successfully'}), 200
    return jsonify({'error': 'Password update failed'}), 400
