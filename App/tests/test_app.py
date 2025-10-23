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

    # def test_shift_toJSON(self):    #need to resolve issue with shift_id attribute
    #     shift = Shift(1, "today", "09:00", "17:00")
    #     shift.set_shift_id(3)
    #     print(f"shift id: {shift.shift_id}")

    #     shift_json = shift.get_json()
    #     self.assertDictEqual(shift_json, {
    #         'shiftId': self.shift_id,
    #         'staffId': self.staff_id,
    #         'date': self.date,
    #         'startTime': self.start_time,
    #         'endTime': self.end_time
    #         } )

class TimeEntryUnitTests(unittest.TestCase):
    def test_timeentry_creation(self):
        timeentry = TimeEntry(1, "08:00")
        assert timeentry.time_in == "08:00"

    # def test_timeentry_toJSON(self):   #need to resolve issue with timeentry_id attribute
    #     timeentry = TimeEntry(1, "08:00", "19:00")
    #     timeentry.set_id(100)
    #     print(f"timeentry id: {timeentry.shift_id}")
    #     timeentry_json = timeentry.get_json()
    #     self.assertDictEqual(timeentry_json, {
    #         'id': self.id,
    #         'shiftId': self.shift_id,
    #         'timeIn': self.time_in,
    #         'timeOut': self.time_out
    #         })


class UserUnitTests(unittest.TestCase): #passed
    def test_user_creation(self):
        user = User("bob", "bobpass")
        assert user.username == "bob"
        assert user.check_password("bobpass")

    def test_user_toJSON(self):
        user = User("bob", "bobpass")
        user_json = user.get_json()
        self.assertDictEqual(user_json, {"id":None, "username":"bob"})
    
 
'''
    Integration Tests
'''
'''
# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()

def test_authenticate():
    user = create_user("bob", "bobpass")
    assert login("bob", "bobpass") != None

class UsersIntegrationTests(unittest.TestCase):

    def test_create_user(self):
        user = create_user("rick", "bobpass")
        assert user.username == "rick"

    def test_get_all_users_json(self):
        users_json = get_all_users_json()
        self.assertListEqual([{"id":1, "username":"bob"}, {"id":2, "username":"rick"}], users_json)

    # Tests data changes in the database
    def test_update_user(self):
        update_user(1, "ronnie")
        user = get_user(1)
        assert user.username == "ronnie"
        
'''