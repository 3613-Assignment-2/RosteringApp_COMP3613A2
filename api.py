from flask import Flask, jsonify, request
from App.controllers.auth import login
from App.controllers.controllers import (
    authenticate, 
    schedule_shift, 
    view_roster, 
    time_in, 
    time_out, 
    view_shift_report, 
    change_password
)
from App.models.staff import Staff

app = Flask("Rostr")

@app.route("/login", methods=['GET', 'POST', 'PUT'])
def test_login():
    staff = Staff("john", "1234", "Staff")
    print(staff.username)
    access_token = login(staff.username, staff.password) #where access_token = JWT token
    if access_token is not None:     
        return jsonify({"access token": access_token}), 200
    else:
        return jsonify({"message": "invalid credentials"}), 401

@app.route("/schedule", methods=['GET', 'POST', 'PUT'])
def test_view_roster():
    staff = Staff("john", "1234", "Staff")
    access_token = login(staff.username, staff.password)
    



# test_schedule_shift()
# test_time_in()
# test_time_out()
# test_view_report()



if __name__ == '__main__':
    app.run(debug=True)
