from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class Staff(db.Model):
    __tablename__ = "staff"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False) 

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)    

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password) 
    
    
    def __init__(self, username, password, role):
        self.username = username
        self.set_password(password)
        self.role = role        
