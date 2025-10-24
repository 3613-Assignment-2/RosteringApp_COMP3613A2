from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user

from.index import index_views

from App.controllers import ( #switch to staff functions
    create_user,
    get_all_users,
    get_all_users_json,
    jwt_required
)

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

@staff_views.route('/staff', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

@staff_views.route('/staff', methods=['POST'])
def create_user_action():
    data = request.form
    flash(f"User {data['username']} created!")
    create_user(data['username'], data['password'])
    return redirect(url_for('user_views.get_user_page'))

@staff_views.route('/api/staff', methods=['GET'])
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)

@staff_views.route('/api/staff', methods=['POST'])
def create_user_endpoint():
    data = request.json
    user = create_user(data['username'], data['password'])
    return jsonify({'message': f"user {user.username} created with id {user.id}"})

@staff_views.route('/static/staff', methods=['GET'])
def static_user_page():
  return send_from_directory('static', 'static-user.html')