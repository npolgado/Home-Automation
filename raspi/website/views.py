from sqlalchemy.orm.exc import NoResultFound
from flask import Blueprint, render_template, request, flash, jsonify
from flask import abort, redirect, url_for
from .models import Daily, Bed, Bath, Beyond, Event
from . import db

try:
    import RPi.GPIO as GPIO
except Exception as e:
    print(f"\n[ERROR] {e}\n")
    pass

import json
import datetime
import urllib
import urllib.request
from bs4 import BeautifulSoup
import os, time, sys, math, re
import subprocess
import datetime
import platform
import requests
from string import Template
import time

views = Blueprint('views', __name__)

PAUSE = 0.3
daily_source = "https://fuckinghomepage.com/"

uno_bedroom_ip = "192.168.1.229"

pattern = '"playabilityStatus":{"status":"ERROR","reason":"Video unavailable"'

def clock_start():
    return time.monotonic()

def clock_end(st):
    print(f"\n[LOG] Completed Backend in {float(time.monotonic() - st)*1000} ms\n")

def ping_target(host):
    target_os = str(platform.platform())
    if bool(re.match("(?i)windows", target_os)):
        os_ping_count = '-n'
    else: os_ping_count = '-c'

    ping_out = subprocess.Popen(
        ['ping', os_ping_count, '1', str(host)],
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT
    )

    stdout, stderr = ping_out.communicate()

    if ping_out.returncode == 0:
        return True
    else:
        return False

def extract_daily(source):
    LINKS = []
    page = urllib.request.urlopen(source)
    soup = BeautifulSoup(page, features="lxml")
    for link in soup.findAll('a'):
        LINKS.append(link.get('href'))
    LINKS = LINKS[1:6]
    return LINKS

def get_video_name(source):
    try:
        VideoID = str(source).split("=")[1]
        params = {"format": "json",
                  "url": "https://www.youtube.com/watch?v=%s" % VideoID}
        url = "https://www.youtube.com/oembed"
        query_string = urllib.parse.urlencode(params)
        url = url + "?" + query_string
        with urllib.request.urlopen(url) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            # pprint.pprint(data)
            return data['title']
    except:
        return "Random Video"

def is_url_ok(url):
    request = requests.get(url)
    return False if pattern in request.text else True

def get_title(url):
    print(f"\n[LOG]GETTING TITLE FOR {url[17:]}\n")
    response = requests.get(url[17:])
    tmp = ''
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        tmp = soup.title.string
    else:
        tmp = 'Article'
    return tmp

@views.route('/', methods=['GET'])
def home():
    st = clock_start()
    try:
        t1 = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        t2 = str(f"{platform.node()}: {platform.machine()} -- {platform.platform()}")
        t3 = str(f"hi ")
    except Exception as e:
        print(f"ERROR:\n{e}")

    templateData = {
        'tracker_1': t1,
        'tracker_1_desc': 'Exact Moment We Out Here',
        'tracker_2': t2,
        'tracker_2_desc': 'What Is Running This Poopy Serber',
        'tracker_3': t3,
        'tracker_3_desc': "Deez Nuts"
    }   

    clock_end(st)
    return render_template("home.html", **templateData)

@views.route('/links', methods=['GET'])
def links():
    st = clock_start()

    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    yesterday = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

    timeString = now.strftime("%Y-%m-%d %H:%M")

    # find a db entry from same time as current page
    try:
        last_pull = Daily.query.filter(Daily.date >= yesterday).first()
    except:
        last_pull = None

    if last_pull:
        # formatting data to be sent returned
        templateData = {
            'title': 'mancave',
            'time': timeString,
            'article': last_pull.article,
            'article_title': last_pull.article_title,
            'book': last_pull.book,
            'gift': last_pull.gift,
            'website': last_pull.weblink,
            'video': last_pull.video,
            'v_title': last_pull.video_title
        }
    else:
        links = extract_daily(daily_source)
        vt = get_video_name(links[4])
        at = get_title(links[0])

        new_entry = Daily(article=links[0],
            article_title=at,
            book=links[1],
            gift=links[2],
            weblink=links[3],
            video=links[4],
            video_title=vt,
            date=now
        )
        try:
            duplicate = Daily.query.filter(Daily.article == new_entry.article,
                Daily.article_title == new_entry.article_title,
                Daily.book == new_entry.book, 
                Daily.gift == new_entry.gift,
                Daily.weblink == new_entry.weblink,
                Daily.video == new_entry.video,
                Daily.video_title == new_entry.video_title
            ).first()
            if duplicate: pass
            else:
                db.session.add(new_entry)
                db.session.commit()
        except Exception as e:
            print(f"\n[ERROR]\n{e}\n")
            db.session.rollback()

        # formatting data to be sent returned
        templateData = {
            'title': 'mancave',
            'time': timeString,
            'article': links[0],
            'article_title': at,
            'book': links[1],
            'gift': links[2],
            'website': links[3],
            'video': links[4],
            'v_title': vt
        }

    clock_end(st)
    return render_template("links.html", **templateData)

@views.route('/led_on')
def led_on():
    st = clock_start()
    transmit = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'transmit.py')
    cmd = transmit + " 10011111"
    cmd = '{} {} {}'.format('sudo', 'python', cmd)
    print(f"running command {cmd}")
    # os.system(cmd)
    clock_end(st)
    return redirect(url_for('views.home'))

@views.route('/alerts', methods=['GET', 'POST'])
def alerts():
    st = clock_start()
    print("\n[LOG] DO BACKEND\n")
    if request.method == 'POST':
        color = request.form['color']
        fast = request.form['en_fast_flashing']
        flush = request.form['en_flush']

        clock_end(st)
        return redirect(url_for('views.home'))
    clock_end(st)
    return render_template("alerts.html")

@views.route('/gpio/<string:id>/<string:level>')
def setPinLevel(id, level):
    st = clock_start()
    try:
        GPIO.output(int(id), int(level))
    except Exception as e:
        print(f"\n[ERROR] {e}\n")
        clock_end(st)
        return "ERROR"

    clock_end(st)
    return "OK"

@views.route('/Bed/<humididy>-<temp>-<heat_index>-<led_state>', methods=['GET', 'POST'])
def bed_collect(area, humididy, temp, heat_index, led_state):
    st = clock_start()
    now = datetime.datetime.now()

    print('\n[LOG] received from {}\nHumidity {}, Temp {}, Heat Index {}\n'.format(request.remote_addr, humididy, temp, heat_index))    
    
    new_reading = Bed(date=now,
        sensor_humidity = float(humididy),
        sensor_temperature = float(temp),
        sensor_heat_index = float(heat_index),
        sensor_led_state = int(led_state)
    )

    try:
        print("\n[LOG] adding to db\n")
        db.session.add(new_reading)
        db.session.commit()
    except Exception as e:
        print(f"\n[ERROR]\n{e}\n")
        db.session.rollback()

    clock_end(st)
    return redirect(url_for('views.sensor_history'))

@views.route('/links-history', methods=['GET'])
def links_history():
    st = clock_start()
    pull = Daily.query.all()
    clock_end(st)
    return render_template("links-history.html", all_dailies=pull)

@views.route('/sensor-history', methods=['GET'])    # TODO: Change this to pull all sensor data
def sensor_history():
    st = clock_start()
    pull = Bed.query.all()
    clock_end(st)
    return render_template("bed.html", all_readings=pull)

@views.route('/delete/<string:area>/<db_entry_date>', methods=['GET'])
def db_delete(area, db_entry_date):
    st = clock_start()
    print(f"\n[LOG] attempting to remove db entry from \n{area} @ {db_entry_date}\n")
    redirect_is = 'views.sensor_history'

    if area == "Bed":
        query = Bed.query.filter(Bed.date == db_entry_date).first()
    elif area == "Bath":
        query = Bath.query.filter(Bath.date == db_entry_date).first()
    elif area == "Beyond":
        query = Beyond.query.filter(Beyond.date == db_entry_date).first()
    elif area == "Daily":
        query = Daily.query.filter(Daily.date == db_entry_date).first()
        redirect_is = 'views.links_history'
    else:
        clock_end(st) 
        return redirect(url_for('views.home'))

    if query:
        print(f"\n[LOG] removing {query}...\n")
        try:
            db.session.delete(query)
            db.session.commit()
        except Exception as e:
            print(f"\n[ERROR]\n{e}\n")
            db.session.rollback()
    else: print(f"\n[LOG] couldn't find query...")

    clock_end(st)
    return redirect(url_for(redirect_is))

@views.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404