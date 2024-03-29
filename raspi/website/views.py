from flask import (Blueprint, abort, flash, jsonify, redirect, render_template,
                   request, url_for)
from sqlalchemy.orm.exc import NoResultFound

from . import db
from .models import Daily, Event, Home

try:
    import RPi.GPIO as GPIO
except Exception as e:
    print(f"\n[ERROR] {e}\n")
    pass

import datetime
import json
import os
import platform
import re
import subprocess
import sys
import time
import urllib
import urllib.request
from string import Template
import numpy as np

import openai
import requests
from bs4 import BeautifulSoup

# Load your API key from an environment variable or secret management service
openai.api_key = os.getenv("OPENAI_API_KEY")

views = Blueprint('views', __name__)

PAUSE = 0.3
daily_source = "https://fuckinghomepage.com/"

uno_bedroom_ip = "192.168.1.229"

pattern = '"playabilityStatus":{"status":"ERROR","reason":"Video unavailable"'

AREAS = ['Bed',
    'Bath',
    'Beyond',
    'PC'
]

DATATYPES = ['sensor_humidity',
    'sensor_temperature',
    'sensor_heat_index',
    'sensor_led_state',
    'sensor_volume',
    'sensor_motion_detected',
    'node_mode',
    'node_status'
]

NODE_MODE = {
    0: "Normal",
    1: "Low Power",
    2: "Off",    
}

NODE_STATUS = {
    0: "ACTIVE",
    1: "ERROR",
    2: "STANDBY",
    3: "DHT_ERROR",
    4: "MOTION_ERROR",
    5: "MICROPHONE_ERROR",
    6: "IR_ERROR"
}

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

@views.route('/assistant', methods=['GET'])
def assistant():
    st = clock_start()
    clock_end(st)
    return render_template("home_assist.html")

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
                print("\n[LOG] updating db...")
                db.session.add(new_entry)
                db.session.commit()
                print("\n[LOG] db updated!\n")
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
def set_pin_level(id, level):
    st = clock_start()
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.output(int(id), int(level))
    except Exception as e:
        print(f"\n[ERROR] {e}\n")
        clock_end(st)
        return "ERROR"

    clock_end(st)
    return "OK"

@views.route('/links-history', methods=['GET'])
def links_history():
    st = clock_start()
    pull = Daily.query.all()
    clock_end(st)
    return render_template("links-history.html", all_dailies=pull)

@views.route('/sensor-history', methods=['GET'])
def sensor_history():
    st = clock_start() 
    pull = Home.query.all()
    clock_end(st)
    return render_template("sensor-history.html", all_readings=pull)

@views.route('/log/<string:area>/<data_0>-<data_1>-<data_2>-<data_3>-<data_4>-<data_5>-<data_6>-<data_7>', methods=['GET', 'POST'])
def db_collect(area, data_0, data_1, data_2, data_3, data_4, data_5, data_6, data_7):
    st = clock_start()
    now = datetime.datetime.now()

    print('\n[LOG] received from {}\n{} - {} - {} - {} - {} - {} - {} - {}\n'.format(request.remote_addr,
        data_0, data_1, data_2, data_3, data_4, data_5, data_6, data_7
        )
    )
    try:
        str_mode = NODE_MODE[int(data_6)]
        str_status = NODE_STATUS[int(data_7)]
    except Exception as e:
        print("\n[ERROR] couldn't find node status or mode...\n")
        str_mode = int(data_6)
        str_status = int(data_7)
    
    new_reading = Home(date=now,
        type = area,
        sensor_humidity = float(data_0),
        sensor_temperature = float(data_1),
        sensor_heat_index = float(data_2),
        sensor_led_state = format(int(data_3), 'b'),
        sensor_volume = float(data_4),
        sensor_motion_detected = bool(int(data_5)),
        node_mode = str_mode,
        node_status = str_status,
    )

    try:
        print("\n[LOG] adding to db...")
        db.session.add(new_reading)
        db.session.commit()
        print("\n[LOG] db updated!\n")
    except Exception as e:
        print(f"\n[ERROR]\n{e}\n")
        db.session.rollback()

    clock_end(st)
    return redirect(url_for('views.sensor_history'))

@views.route('/delete/<string:area>/<db_entry_date>', methods=['GET'])
def db_delete(area, db_entry_date):
    st = clock_start()
    print(f"\n[LOG] attempting to remove db entry from \n{area} @ {db_entry_date}\n")
    redirect_is = 'views.sensor_history'
    
    if area == "Home":
        query = Home.query.filter(Home.date == db_entry_date).first()
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

@views.route("/chart", methods=['GET', 'POST'])
def chart():
    global DATATYPES, AREAS

    if request.method == 'POST':
        area = str(request.form.get("area"))
        column = request.form.get('datatype')
        pull = Home.query.filter_by(type = area).all()
        labels = [str(h.date) for h in pull]
        data = [x for x in range(len(labels))]

        if column == 'sensor_humidity': data = [h.sensor_humidity for h in pull]
        if column == 'sensor_temperature': data = [h.sensor_temperature for h in pull]
        if column == 'sensor_heat_index': data = [h.sensor_heat_index for h in pull]
        if column == 'sensor_led_state': data = [h.sensor_led_state for h in pull]
        if column == 'sensor_volume': data = [h.sensor_volume for h in pull]
        if column == 'sensor_motion_detected': data = [h.sensor_motion_detected for h in pull]
        if column == 'node_mode': data = [h.node_mode for h in pull]
        if column == 'node_status': data = [h.node_status for h in pull] 

        templateData = {
            'labels': labels,
            'data': data,
            'areas': AREAS,
            'datatypes': DATATYPES
        } 

        return render_template("sensor-chart.html", **templateData)

    try:
        t_labels = request.form.get("labels")
        t_data = request.form.get("data")
        if t_labels and t_data:
            templateData = {
                'labels': t_labels,
                'data': t_data,
                'areas': AREAS,
                'datatypes': DATATYPES
            }
        else:
            templateData = {
                'labels': [0,1],
                'data': [1,1],
                'areas': AREAS,
                'datatypes': DATATYPES
            }
    except Exception as e:
        templateData = {
            'labels': [0,1],
            'data': [1,1],
            'areas': AREAS,
            'datatypes': DATATYPES
        } 

    return render_template("sensor-chart.html", **templateData)

@views.route("/gpt/completions", methods=['GET', 'POST'])
def query():
    st = clock_start()
    if request.method == 'POST':
        print("[LOG] getting form data...")
        prompt = str(request.form.get("prompt"))
        max_length = int(request.form.get("max_length"))
        temp = float(request.form.get("temperature"))
        number_time = int(request.form.get("number_choices"))

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=temp,
            max_tokens=max_length,
            echo=True,
            best_of=number_time
        )

        print("[LOG] FOUND {} RESPONSES".format(len(response["choices"])))
        answer = response["choices"][0]["text"]

        templateData = {
            'prompt': prompt,
            'max_length': max_length,
            'temperature': temp,
            'number_choices': number_time,
            'response': answer
        } 
        clock_end(st)
        return render_template("gpt_completions.html", **templateData)
    
    print("[LOG] loading fresh completion query")
    templateData = {
        'prompt': "Ahoy Land Lover!! Release Thou Gold",
        'max_length': 100,
        'temperature': 0.1,
        'number_choices': 1,
        'response': 'Output:'
    }

    clock_end(st)
    return render_template("gpt_completions.html", **templateData)

@views.route("/gpt/images", methods=['GET', 'POST'])
def query_image():
    st = clock_start()
    if request.method == 'POST':
        prompt = str(request.form.get("prompt"))
        num_images = int(request.form.get("num_images"))
        width = int(request.form.get("image_width"))
        height = int(request.form.get("image_height"))
        image_size = str(f"{width}x{height}")
        print(f"[LOG] got form data...\nPrompt:\t{prompt}\nNumber of Images:\t{num_images}\nWidth:\t\t{width}\nHeight:\t\t{height}")

        response = openai.Image.create(
            prompt=prompt,
            n=num_images,
            size=image_size
        )

        print("[LOG] FOUND {} RESPONSES".format(len(np.array(response['data']))))
        image_urls = np.array(response['data'])
        # sys.exit()

        templateData = {
            'prompt': prompt,
            'num_images': num_images,
            'image_width': width,
            'image_height': height,
            'results': image_urls
        } 
        clock_end(st)
        return render_template("gpt_images.html", **templateData)

    print("[LOG] loading fresh query page")
    templateData = {
        'prompt': str("a bumble bee fighting a carrot on the moon"),
        'num_images': 1,
        'image_width': 1024,
        'image_height': 1024,
        'results': list()
    } 

    clock_end(st)
    return render_template("gpt_images.html", **templateData)

@views.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
