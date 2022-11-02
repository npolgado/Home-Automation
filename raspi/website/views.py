from flask import Blueprint, render_template, request, flash, jsonify
from flask import abort, redirect, url_for
from .models import Daily
from . import db
import json
import datetime
import urllib
from bs4 import BeautifulSoup
import lxml
import pprint
import urllib.request
import os, sys
import datetime
from datetime import date

views = Blueprint('views', __name__)

PAUSE = 0.3
daily_source = "https://fuckinghomepage.com/"

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
    return render_template("home.html")

@views.route('/links-history', methods=['GET'])
def links_history():
    return render_template("table.html", all_dailies=Daily.query.all())

@views.route('/links', methods=['GET'])
def links():
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    timeString = now.strftime("%Y-%m-%d %H:%M")
    # print("\n\ntoday = {}\n".format(now))
    # print("yesterday = {}".format(yesterday))
    # print("\n QUERY=\n\n {}".format(Daily.query.filter(Daily.date >= yesterday).first_or_404()))

    try:
        # finds first db entry thats within 24 hours of now
        last_pull = Daily.query.filter(Daily.date >= yesterday).first()
    except:
        last_pull = None
    if last_pull:
        daily_links = last_pull

        # formatting data to be sent returned
        templateData = {
            'title': 'mancave',
            'time': timeString,
            'article': daily_links.article,
            'book': daily_links.book,
            'gift': daily_links.gift,
            'website': daily_links.weblink,
            'video': daily_links.video,
            'v_title': daily_links.video_title
        }
    else:
        # time data
        links = extract_daily(daily_source)

        new_daily = Daily(article=links[0],
            book=links[1],
            gift=links[2],
            weblink=links[3],
            video=links[4],
            video_title=get_video_name(links[4]),
            date=now
        )

        print(f"\n{new_daily.article}\n{new_daily.book}\n{new_daily.date}\n{new_daily.gift}\n{new_daily.video}\n{new_daily.video_title}\n{new_daily.weblink}\n")
        db.session.add(new_daily)
        db.session.commit()

        # formatting data to be sent returned
        templateData = {
            'title': 'mancave',
            'time': timeString,
            'article': new_daily.article,
            'book': new_daily.book,
            'gift': new_daily.gift,
            'website': new_daily.weblink,
            'video': new_daily.video,
            'v_title': new_daily.video_title
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