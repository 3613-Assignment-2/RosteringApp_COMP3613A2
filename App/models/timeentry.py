from App.database import db

class TimeEntry(db.Model):
    __tablename__ = "time_entries"

    id = db.Column(db.Integer, primary_key=True)
    shift_id = db.Column(db.Integer, db.ForeignKey("shifts.shift_id"), nullable=False)
    time_in = db.Column(db.Time, nullable=True)
    time_out = db.Column(db.Time, nullable=True)

    def __init__(self, shift_id, time_in=None, time_out=None):
        self.shift_id = shift_id
        self.time_in = time_in
        self.time_out = time_out   

    def set_id(self, id):
        self.id = id

    def get_json(self):
        return {
            'id': self.id,
            'shiftId': self.shift_id,
            'timeIn': self.time_in,
            'timeOut': self.time_out
        }       
