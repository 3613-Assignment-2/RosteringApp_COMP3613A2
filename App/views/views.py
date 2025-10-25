from flask import Blueprint, request, jsonify
from App.models.staff import Staff
from App.models.shift import Shift
from App.models.timeentry import TimeEntry
from App.controllers.controllers import (
    authenticate, schedule_shift, view_roster, time_in, time_out, view_shift_report, change_password
)
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity


views = Blueprint('views', __name__)

@views.route('/login', methods=['POST'])
def login_route():
    data = request.get_json()
    print(data)
    username = data.get('username')
    password = data.get('password')

    user = authenticate(username, password)
    if not user:
        return jsonify(message="Invalid credentials"), 401

    access_token = create_access_token(identity=user.username)
    return jsonify(access_token=access_token), 200

@views.route('/view_roster', methods=['POST'])
@jwt_required()
def view_roster_route():
    current_user = get_jwt_identity()
    user = Staff.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401
    if user.role != "Staff":
        return jsonify({'error': 'Only Staff can view the roster'}), 401

    roster = view_roster(user)
    return jsonify({'roster': roster}), 200

@views.route('/schedule', methods=['POST'])
@jwt_required()
def schedule_shift_route():

    current_user = get_jwt_identity()
    admin = Staff.query.filter_by(username=current_user).first()
    if not admin or admin.role != "Admin":
        return jsonify({'error': 'Only Admins can schedule shifts'}), 401
    data = request.json
    staff_username = data.get('staff_username')
    date = data.get('date')
    start_time = data.get('start_time')
    end_time = data.get('end_time')

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
@jwt_required()
def time_in_route():

    current_user = get_jwt_identity()
    user = Staff.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401
    if user.role != "Staff":
        return jsonify({'error': 'Only Staff can time in'}), 401
    
    shift_id = request.json.get('shift_id')
    entry = time_in(user, shift_id)
    if entry:
        return jsonify({'time_in': entry.time_in.isoformat()}), 200
    return jsonify({'error': 'Time in failed'}), 400

@views.route('/time_out', methods=['POST'])
@jwt_required()
def time_out_route():
    

    current_user = get_jwt_identity()
    user = Staff.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401
    if user.role != "Staff":
        return jsonify({'error': 'Only Staff can time out'}), 401

    shift_id = request.json.get('shift_id')
    entry = time_out(user, shift_id)
    if entry:
        return jsonify({'time_out': entry.time_out.isoformat()}), 200
    return jsonify({'error': 'Time out failed'}), 400

@views.route('/view_report', methods=['POST'])
@jwt_required()
def view_report_route():

    current_user = get_jwt_identity()
    admin = Staff.query.filter_by(username=current_user).first()
    if not admin or admin.role != 'Admin':
        return jsonify({'error': 'Only Admins can view reports'}), 401

    report = view_shift_report(admin)
    return jsonify({'report': report}), 200

@views.route('/change_password', methods=['POST'])
@jwt_required()
def change_password_route():
    data = request.json
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    success = change_password(username, old_password, new_password)
    if success:
        return jsonify({'message': 'Password updated successfully'}), 200
    return jsonify({'error': 'Password update failed'}), 400

@views.route('/add_staff', methods=['POST'])
@jwt_required()
def add_staff_route():

    current_user = get_jwt_identity()
    admin = Staff.query.filter_by(username=current_user).first()
    if not admin or admin.role != 'Admin':
        return jsonify({'error': 'Only Admins can add staff'}), 401
    
    data = request.json
    new_username = data.get('username')
    new_password = data.get('password')
    if Staff.query.filter_by(username=new_username).first():
        return jsonify({'error': 'User already exists'}), 400

    staff = Staff(username=new_username, password=new_password, role='Staff')
    from App.database import db
    db.session.add(staff)
    db.session.commit()
    return jsonify({'message': f'User {new_username} added successfully'}), 200

