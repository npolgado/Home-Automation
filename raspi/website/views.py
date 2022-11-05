from sqlalchemy.orm.exc import NoResultFound
from flask import Blueprint, render_template, request, flash, jsonify
from flask import abort, redirect, url_for
from .models import Daily
from . import db
import json
import datetime
import urllib
from bs4 import BeautifulSoup
import urllib.request
import os
import datetime
import platform

views = Blueprint('views', __name__)

PAUSE = 0.3
daily_source = "https://fuckinghomepage.com/"

def get_or_create(model, **kwargs):
    """
    SOURCE = https://stackoverflow.com/questions/44511046/sqlalchemy-prevent-duplicate-rows
    Usage:
    class Employee(Base):
        __tablename__ = 'employee'
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)

    get_or_create(Employee, name='bob')
    """
    instance = get_instance(model, **kwargs)
    if instance is None:
        instance = create_instance(model, **kwargs)
    return instance

def create_instance(model, **kwargs):
    """
    SOURCE = https://stackoverflow.com/questions/44511046/sqlalchemy-prevent-duplicate-rows
    create instance
    """
    try:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.flush()
    except Exception as msg:
        mtext = 'model:{}, args:{} => msg:{}'
        # log.error(mtext.format(model, kwargs, msg))
        db.session.rollback()
        raise(msg)
    return instance

def get_instance(model, **kwargs):
    """
    SOURCE = https://stackoverflow.com/questions/44511046/sqlalchemy-prevent-duplicate-rows
    Return first instance found.
    """
    try:
        return db.session.query(model).filter(**kwargs).first()
    except NoResultFound:
        return None

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

@views.route('/', methods=['GET'])
def home():
    print(request.args)
    try:
        t1 = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        t2 = str(f"{platform.machine()} - {platform.platform()} - {platform.processor()}")
        t3 = str(f"hi {platform.node()}")
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
    return render_template("home.html", **templateData)

@views.route('/links-history', methods=['GET'])
def links_history():
    return render_template("table.html", all_dailies=Daily.query.all())

@views.route('/links', methods=['GET'])
def links():
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=0.5)
    timeString = now.strftime("%Y-%m-%d %H:%M")

    last_pull = get_instance(Daily, (Daily.date <= yesterday))
    print(last_pull)

    if last_pull[0]:

        # formatting data to be sent returned
        templateData = {
            'title': 'mancave',
            'time': timeString,
            'article': last_pull.article,
            'book': last_pull.book,
            'gift': last_pull.gift,
            'website': last_pull.weblink,
            'video': last_pull.video,
            'v_title': last_pull.video_title
        }
    else:
        # time data
        links = extract_daily(daily_source)
        vt = get_video_name(links[4])

        get_or_create(Daily, article=links[0],
            book=links[1],
            gift=links[2],
            weblink=links[3],
            video=links[4],
            video_title=vt,
            date=now
        )

        # formatting data to be sent returned
        templateData = {
            'title': 'mancave',
            'time': timeString,
            'article': links[0],
            'book': links[1],
            'gift': links[2],
            'website': links[3],
            'video': links[4],
            'v_title': vt
        }

    return render_template("links.html", **templateData)

@views.route('/led_on')
def led_on():
    transmit = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'transmit.py')
    cmd = transmit + " 10011111"
    cmd = '{} {} {}'.format('sudo', 'python', cmd)
    print(f"running command {cmd}")
    # os.system(cmd)
    return redirect(url_for('views.home'))

@views.route('/alerts', methods=['GET', 'POST'])
def alerts():
    print("DO BACKEND")
    if request.method == 'POST':
        color = request.form['color']
        fast = request.form['en_fast_flashing']
        flush = request.form['en_flush']

        # TODO: generate transmit.py command

        return redirect(url_for('views.home'))
    return render_template("alerts.html")

@views.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404