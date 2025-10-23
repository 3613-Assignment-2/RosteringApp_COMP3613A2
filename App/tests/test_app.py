import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import *
from App.models.staff import Staff
from App.models.user import User
from App.models.shift import Shift
from App.models.timeentry import TimeEntry
from App.controllers import (
    create_user,
    get_all_users_json,
    login,
    get_user,
    get_user_by_username,
    update_user
)
from App.controllers.controllers import (
    time_in,
    time_out,
    change_password,
    authenticate,
    schedule_shift,
    view_roster,
    view_shift_report,
    add_staff
)



LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
# @pytest.fixture
# def db_initialize():


class StaffUnitTests(unittest.TestCase): #all passed

    def test_new_staff(self):
        staff = Staff("john", "1234", "Staff")
        assert staff.username == "john"
        assert staff.role == "Staff"

    def test_set_password(self):
        staff = Staff("john", "1234", "Staff")
        staff.set_password("mypassword")
        assert staff.password != "mypassword"  #since password is hashed

    def test_check_password_valid(self):
        staff = Staff("john", "1234", "Staff")
        staff.set_password("mypassword")
        assert staff.check_password("mypassword")
    
    def test_check_password_invalid(self):
        staff = Staff("john", "1234", "Staff")
        staff.set_password("mypassword")
        assert not staff.check_password("wrongpass")


class ShiftUnitTests(unittest.TestCase):
    def test_shift_creation(self):
        shift = Shift(1, "today", "09:00", "17:00")
        assert shift.staff_id == 1
        assert shift.start_time == "09:00"
        assert shift.end_time == "17:00"

    def test_shift_toJSON(self):    #need to resolve issue with shift_id attribute
        shift = Shift(1, "today", "09:00", "17:00")
        shift.set_shift_id(3)
        print(f"shift id: {shift.shift_id}")

        shift_json = shift.get_json()
        self.assertDictEqual(shift_json, {
            'shiftId': shift.shift_id,
            'staffId': shift.staff_id,
            'date': shift.date,
            'startTime': shift.start_time,
            'endTime': shift.end_time
            } )

class TimeEntryUnitTests(unittest.TestCase):
    def test_timeentry_creation(self):
        timeentry = TimeEntry(1, "08:00")
        assert timeentry.time_in == "08:00"

    def test_timeentry_toJSON(self):   #need to resolve issue with timeentry_id attribute
        timeentry = TimeEntry(1, "08:00", "19:00")
        timeentry.set_id(100)
        print(f"timeentry id: {timeentry.shift_id}")
        timeentry_json = timeentry.get_json()
        self.assertDictEqual(timeentry_json, {
            'id': timeentry.id,
            'shiftId': timeentry.shift_id,
            'timeIn': timeentry.time_in,
            'timeOut': timeentry.time_out
            })


class UserUnitTests(unittest.TestCase): #passed
    def test_user_creation(self):
        user = User("bob", "bobpass")
        assert user.username == "bob"
        assert user.check_password("bobpass")

    def test_user_toJSON(self):
        user = User("bob", "bobpass")
        user_json = user.get_json()
        self.assertDictEqual(user_json, {"id":None, "username":"bob"})
    
 

@pytest.fixture(scope="module")
def client():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield app.test_client()
    with app.app_context():
        db.session.remove()
        db.drop_all()

class IntegrationTests(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()

        self.admin = Staff(username="admin1", password="adminpass", role="Admin")
        self.staff = Staff(username="staff1", password="staffpass", role="Staff")
        db.session.add_all([self.admin, self.staff])
        db.session.commit()
        db.session.refresh(self.staff) 


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login(self):
        token = authenticate("staff1", "staffpass")
        assert token is not None

        bad_token = authenticate("staff1", "wrongpass")
        assert bad_token is None

    def test_view_roster(self):
        schedule_shift(self.admin, self.staff, "23-10-2025", "09:00", "17:00")
        staff_roster = view_roster(self.staff)
        assert isinstance(staff_roster, list)
        assert len(staff_roster) > 0

        admin_roster = view_roster(self.admin)
        assert admin_roster is None or admin_roster == []

    def test_schedule_shift(self):
        shift = schedule_shift(self.admin, self.staff, "23-10-2025", "09:00", "17:00")
        assert shift.staff_id == self.staff.user_id

    def test_time_in(self):
        shift = schedule_shift(self.admin, self.staff, "23-10-2025", "09:00", "17:00")
        entry = time_in(self.staff, shift.shift_id)
        assert entry.time_in is not None

    def test_time_out(self):
        shift = schedule_shift(self.admin, self.staff, "23-10-2025", "09:00", "17:00")
        time_in(self.staff, shift.shift_id)
        entry = time_out(self.staff, shift.shift_id)
        assert entry.time_out is not None

    def test_view_report(self):
        shift = schedule_shift(self.admin, self.staff, "23-10-2025", "09:00", "17:00")
        time_in(self.staff, shift.shift_id)
        time_out(self.staff, shift.shift_id)
        report = view_shift_report(self.admin)
        assert isinstance(report, list)
        assert len(report) > 0

    def test_change_password(self):
        change_password("staff1", "staffpass", "newpass")
        updated = authenticate("staff1", "newpass")
        assert updated is not None

        failed = authenticate("staff1", "staffpass")
        assert failed is None

    def test_add_staff(self):
        new_staff = add_staff(self.admin, "newstaff", "newpass")
        assert new_staff.username == "newstaff"

    def test_restricted(self):
        unauthorized = view_roster(None)
        assert unauthorized is None or unauthorized == []