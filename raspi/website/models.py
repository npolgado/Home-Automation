from . import db
from sqlalchemy.sql import func

# from raspi import website

# all data coming from https://fuckinghomepage.com
class Daily(db.Model):
    date = db.Column(db.DateTime(timezone=True), default=func.now(), primary_key=True)
    article = db.Column(db.String(300))
    article_title = db.Column(db.String(300))
    book = db.Column(db.String(300))
    gift = db.Column(db.String(300))
    weblink = db.Column(db.String(300))
    video = db.Column(db.String(300))
    video_title = db.Column(db.String(300))

# all data coming from the bedroom
class Bed(db.Model):
    date = db.Column(db.DateTime(timezone=True), default=func.now(), primary_key=True)
    sensor_humidity = db.Column(db.Float)
    sensor_temperature = db.Column(db.Float)
    sensor_heat_index = db.Column(db.Float)
    sensor_led_state = db.Column(db.INT)

# data coming from the bathroom
class Bath(db.Model):
    date = db.Column(db.DateTime(timezone=True), default=func.now(), primary_key=True)
    sensor_humidity = db.Column(db.Float)
    sensor_temperature = db.Column(db.Float)
    sensor_heat_index = db.Column(db.Float)
    sensor_volume = db.Column(db.Integer)

# data coming from the main living room!
class Beyond(db.Model):
    date = db.Column(db.DateTime(timezone=True), default=func.now(), primary_key=True)
    sensor_humidity = db.Column(db.Float)
    sensor_temperature = db.Column(db.Float)
    sensor_heat_index = db.Column(db.Float)
    sensor_volume = db.Column(db.Integer)
    sensor_motion = db.Column(db.Integer)
    sensor_motion_detected = db.Column(db.Boolean)

# db type for the event of 
class Event(db.Model):
    date = db.Column(db.DateTime(timezone=True), default=func.now(), primary_key=True)
    area = db.Column(db.String(300))
    type = db.Column(db.String(300))

# Report of Home based on latest events from Bed, Bath, or Beyond...
# class Home(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.DateTime(timezone=True), default=func.now())
#     temp_bed = db.Column(db.Float)
#     temp_bath = db.Column(db.Float)
#     temp_beyond = db.Column(db.Float)
#     humidity = db.Column(db.Float)
#     sound = db.Column(db.Float)
#     light = db.Column(db.Float)

''' These are based on GPT3'''
# class Home(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.DateTime(timezone=True), default=func.now())
#     temp_bed = db.Column(db.Float)
#     temp_bath = db.Column(db.Float)
#     temp_beyond = db.Column(db.Float)
#     humidity = db.Column(db.Float)
#     sound = db.Column(db.Float)
#     light = db.Column(db.Float)

# # IOT sensor readings for a particular day
# class Sensor(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.DateTime(timezone=True), default=func.now())
#     sensor_type = db.Column(db.String(20))
#     sensor_id = db.Column(db.Integer)
#     sensor_reading = db.Column(db.Float)