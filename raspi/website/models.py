from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# from raspi import website


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    user_name = db.Column(db.String(150))
    notes = db.relationship('Note')

class Daily(db.Model):
    date = db.Column(db.DateTime(timezone=True), default=func.now(), primary_key=True)
    article = db.Column(db.String(300))
    book = db.Column(db.String(300))
    gift = db.Column(db.String(300))
    weblink = db.Column(db.String(300))
    video = db.Column(db.String(300))
    video_title = db.Column(db.String(300))