from sqlalchemy.orm.exc import NoResultFound
from flask import Blueprint, render_template, request, flash, jsonify
from flask import abort, redirect, url_for
from .models import Daily
from . import db
# import RPi.GPIO as GPIO
import json
import datetime
import urllib
from bs4 import BeautifulSoup
import urllib.request
import os
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

@views.route('/links/history', methods=['GET'])
def links_history():
    st = clock_start()
    pull = Daily.query.all()
    clock_end(st)
    return render_template("table.html", all_dailies=pull)

@views.route('/delete/<db_entry_date>', methods=['GET'])
def delete(db_entry_date):
    query = Daily.query.filter(Daily.date == db_entry_date).first()

    if query:
        print(f"\n[LOG] attempting to remove {query}\n")
        try:
            db.session.delete(query)
            db.session.commit()
        except Exception as e:
            print(f"\n[ERROR]\n{e}\n")
            db.session.rollback()
    else: print(f"\n[LOG] couldn't find query...")
    return links_history()

@views.route('/links', methods=['GET'])
def links():
    st = clock_start()
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    yesterday = yesterday.replace(hour=11, minute=59, second=59, microsecond=999999)
    
    timeString = now.strftime("%Y-%m-%d %H:%M")
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
            'article_title': get_title(last_pull.article),
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
            duplicate = Daily.query.filter(Daily.article == new_entry.article, Daily.article_title == new_entry.article_title,
                Daily.book == new_entry.book, Daily.gift == new_entry.gift,
                Daily.weblink == new_entry.weblink, Daily.video == new_entry.video,
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
    GPIO.output(int(id), int(level))
    return "OK"

@views.route('/esp/<humididy>-<temp>-<heat_index>', methods=['GET', 'POST'])
def esp(humididy, temp, heat_index):
    st = clock_start()

    print('\n[LOG] received from {}\nHumidity {}, Temp {}, Heat Index {}\n'.format(request.remote_addr, humididy, temp, heat_index))    

    clock_end(st)
    return ''

@views.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404