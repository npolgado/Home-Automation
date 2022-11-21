from . import db
from sqlalchemy.sql import func

# from raspi import website

class Daily(db.Model):
    date = db.Column(db.DateTime(timezone=True), default=func.now(), primary_key=True)
    article = db.Column(db.String(300))
    article_title = db.Column(db.String(300))
    book = db.Column(db.String(300))
    gift = db.Column(db.String(300))
    weblink = db.Column(db.String(300))
    video = db.Column(db.String(300))
    video_title = db.Column(db.String(300))

# DHT11 Temp / Humidity Sensor Readying from Bedroom
class Bed_Atmosphere(db.Model):
    date = db.Column(db.DateTime(timezone=True), default=func.utcnow(), primary_key=True)
    sensor_reading_humidity = db.Column(db.Float)
    sensor_reading_temperature = db.Column(db.Float)
    sensor_reading_heat_index = db.Column(db.Float)

# GPT3 SUGGESTION DATABASE MODELS
# # averages from IOT sensors around apartment, for trend analysis
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