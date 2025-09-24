from App.database import db

class TimeEntry(db.Model):
    __tablename__ = "time_entries"

    id = db.Column(db.Integer, primary_key=True)
    shift_id = db.Column(db.Integer, db.ForeignKey("shifts.id"), nullable=False)
    time_in = db.Column(db.Time, nullable=True)
    time_out = db.Column(db.Time, nullable=True)

    def __repr__(self):
        return f"<TimeEntry Shift={self.shift_id} In={self.time_in} Out={self.time_out}>"
    
    def get_json(self):
        return {
            'id': self.id,
            'shiftId': self.shift_id,
            'timeIn': self.time_in,
            'timeOut': self.time_out
        }       
    
    def __init__(self, shift_id, time_in=None, time_out=None):
        self.shift_id = shift_id
        self.time_in = time_in
        self.time_out = time_out    

    def update(self, time_in=None, time_out=None):
        if time_in:
            self.time_in = time_in
        if time_out:
            self.time_out = time_out

