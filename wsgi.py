import click
from flask.cli import AppGroup
from App.main import create_app
from App.database import db, get_migrate
from App.controllers.controllers import (
    login, schedule_shift, view_roster, time_in, time_out, view_shift_report
)
from App.models.staff import Staff
from App.models.shift import Shift
from App.models.timeentry import TimeEntry
from datetime import datetime


app = create_app()
migrate = get_migrate(app)

# -------------------------
# Rostering CLI Commands
# -------------------------
rostering_cli = AppGroup('rostering', help='Rostering commands')

@rostering_cli.command("login", help="Login as a user")
@click.argument("username")
@click.argument("password")
def login_command(username, password):
    user = login(username, password)
    if user:
        print(f"Logged in as {user.username} ({user.role})")
    else:
        print("Login failed")

@rostering_cli.command("view_roster", help="View all shifts")
def view_roster_command():
    roster = view_roster()
    for r in roster:
        print(f"Staff: {r['staff']}, Date: {r['date']}, Start: {r['start']}, End: {r['end']}")

@rostering_cli.command("schedule", help="Schedule a shift (Admin only)")
@click.argument("admin_username")
@click.argument("staff_username")
@click.argument("date")
@click.argument("start_time")
@click.argument("end_time")
def schedule_shift_command(admin_username, staff_username, date, start_time, end_time):
    admin = Staff.query.filter_by(username=admin_username).first()
    staff_user = Staff.query.filter_by(username=staff_username).first()
    if not admin or not staff_user:
        print("Admin or staff user not found")
        return
    try:
        shift = schedule_shift(admin, staff_user, date, start_time, end_time)
        print(f"Shift scheduled: Staff={staff_user.username}, Date={shift.date}, Start={shift.start_time}, End={shift.end_time}")
    except Exception as e:
        print(f"Error: {e}")

@rostering_cli.command("time_in", help="Record time in for a shift (Staff only)")
@click.argument("staff_username")
@click.argument("shift_id", type=int)
def time_in_command(staff_username, shift_id):
    staff_user = Staff.query.filter_by(username=staff_username).first()
    if not staff_user:
        print("Staff not found")
        return
    try:
        entry = time_in(staff_user, shift_id)
        print(f"Time in recorded: {entry.time_in}")
    except Exception as e:
        print(f"Error: {e}")

@rostering_cli.command("time_out", help="Record time out for a shift (Staff only)")
@click.argument("staff_username")
@click.argument("shift_id", type=int)
def time_out_command(staff_username, shift_id):
    staff_user = Staff.query.filter_by(username=staff_username).first()
    if not staff_user:
        print("Staff not found")
        return
    try:
        entry = time_out(staff_user, shift_id)
        print(f"Time out recorded: {entry.time_out}")
    except Exception as e:
        print(f"Error: {e}")

@rostering_cli.command("view_report", help="View shift report (Admin only)")
@click.argument("admin_username")
def view_report_command(admin_username):
    admin = Staff.query.filter_by(username=admin_username).first()
    if not admin:
        print("Admin not found")
        return
    try:
        report = view_shift_report(admin)
        for r in report:
            print(f"Staff: {r['staff']}, Date: {r['date']}, Start: {r['start']}, End: {r['end']}")
            for e in r['time_entries']:
                print(f"    Time In: {e['in']}, Time Out: {e['out']}")
    except Exception as e:
        print(f"Error: {e}")

# Add rostering CLI to the app
app.cli.add_command(rostering_cli)

# -------------------------
# Database Initialization CLI
# -------------------------
@app.cli.command("init", help="Creates and initializes the database")
def init():
    db.create_all()
    # Optionally, add some default users
    if not Staff.query.first():
        admin = Staff(username="admin1", password="adminpass", role="Admin")
        staff1 = Staff(username="staff1", password="staffpass", role="Staff")
        db.session.add_all([admin, staff1])
        db.session.commit()
    print("Database initialized with default users")


