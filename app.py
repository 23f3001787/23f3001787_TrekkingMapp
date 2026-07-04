from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)


#user can have many bookings
#one booking by one user

#one trek can have many booking
#one booking is for one trek

#one staff can have many treks
#one trek can have one staff


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='trekker')#admin,staff,trekker
    status = db.Column(db.String(20), nullable=False, default='approved')
    bookings = db.relationship('Booking', backref='user', lazy=True)#staff need approval to login 'pending' then


class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(300),nullable=False)
    difficulty = db.Column(db.String(100),nullable=False)#easy,moderate,hard
    duration_days = db.Column(db.Integer,nullable=False)
    available_slots = db.Column(db.Integer,nullable=False)
    status = db.Column(db.String(100),nullable=False, default='Pending') #pending,approved,open,closed,completed
    staff_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    bookings = db.relationship('Booking', backref='trek', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'))
    status = db.Column(db.String(20),nullable=False, default="Booked")
    booking_date = db.Column(db.DateTime,default=datetime.now)
    
    
    
    
with app.app_context():
    db.create_all()

    admin = User.query.filter_by(role='admin').all()

    if len(admin)==0:
        new_admin = User(
            username='admin',
            email='admin@admin.com',
            password='admin123',
            role='admin',
            status='approved'
        )
        db.session.add(new_admin)
        db.session.commit()
        print('admin account initiated')
        print('startup complete')
    else:
        print('startup complete')

if __name__ == '__main__':
    app.run(debug=True)
    