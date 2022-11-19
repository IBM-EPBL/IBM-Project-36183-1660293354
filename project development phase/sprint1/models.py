from datetime import datetime
from plasma import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id): 
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    contact_no = db.Column(db.String(20), unique=True, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    blood_group = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.contact_no}', '{self.gender}', '{self.role}', '{self.blood_group}')"

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    from_id = db.Column(db.String(120), db.ForeignKey('user.email'))
    to_id = db.Column(db.String(120), db.ForeignKey('user.email'))
    message = db.Column(db.String(100))

    def __repr__(self):
        return f"User('{self.from_id}', '{self.to_id}', '{self.message}')"
