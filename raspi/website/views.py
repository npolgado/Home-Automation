from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Daily
from . import db
import json
import datetime
import urllib
from bs4 import BeautifulSoup
import lxml
import pprint
import urllib.request
import datetime
from datetime import date

views = Blueprint('views', __name__)

PAUSE = 0.3
daily_source = "https://fuckinghomepage.com/"

PARTY = False               # Bedroom LED toggle status
DETECT_TRIGGERED = False    # Motion Sensors bool
TV_TOGGLE = False           # TV on/off


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
            pprint.pprint(data)
            return data['title']
    except:
        return "Random Video"

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/links', methods=['GET'])
def links():
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    timeString = now.strftime("%Y-%m-%d %H:%M")
    print("\n\ntoday = {}\n".format(now))
    print("yesterday = {}".format(yesterday))
    print("\n QUERY=\n\n {}".format(Daily.query.filter(Daily.date >= yesterday).all()))

    if Daily.query.filter(Daily.date >= yesterday).all():
        daily_links = Daily.query.filter(Daily.date >= yesterday).first_or_404()

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
        now = datetime.datetime.now()
        links = extract_daily(daily_source)

        new_daily = Daily(article=links[0],
            book=links[1],
            gift=links[2],
            weblink=links[3],
            video=links[4],
            video_title=get_video_name(links[4])
        )

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

    return render_template("links.html", **templateData, user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
