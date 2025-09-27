from db import db
from datetime import datetime
from sqlalchemy import Column,Integer,ForeignKey,String,Float,DateTime,Enum
import enum


class SpotStatus(enum.Enum):
    O="OCCUPIED"
    A="AVAILABLE"
    

class User(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(50), unique=True, nullable=False) 
    password= db.Column(db.String(200), nullable=False)
    name=db.Column(db.String(50),nullable=False)
    address=db.Column(db.String(100),nullable=False,default='NA')
    pincode=db.Column(db.String(6),nullable=False, default='NA')
    role= db.Column(db.String(50), nullable=False, default='user')

    reservation=db.relationship('Reservation', backref='user',lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'


class ParkingLot(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    prime_location_name=db.Column(db.String(50),nullable=False)
    price=db.Column(db.Float,nullable=False,default=100)
    address=db.Column(db.String(100),nullable=False,default='NA')
    pincode=db.Column(db.String(6),nullable=False, default='NA')
    maximum_number_of_spots=db.Column(db.Integer,default=0)

    spots=db.relationship('ParkingSpot', backref='lot', lazy=True)

    

class ParkingSpot(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    lot_id=db.Column(db.Integer,db.ForeignKey('parking_lot.id'), nullable=False)
    status=db.Column(db.Enum(SpotStatus,native_enum=False), default=SpotStatus.A, nullable=False) # by default A--> Available, O--> occupied
    reservation= db.relationship('Reservation', backref='spot', uselist=False)


class Reservation(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    lot_id=db.Column(db.Integer,db.ForeignKey('parking_lot.id'))
    spot_id=db.Column(db.Integer,db.ForeignKey('parking_spot.id'))
    vehicle_number=db.Column(db.String(25),nullable=False)
    start_time=db.Column(db.DateTime, default=datetime.now)
    end_time=db.Column(db.DateTime, nullable=True)
    cost=db.Column(db.Float, nullable=True)
    
    lot = db.relationship('ParkingLot', backref='reservations')