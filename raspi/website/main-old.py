from flask import Flask, render_template
import datetime, urllib
from bs4 import BeautifulSoup
import lxml
from lxml import etree
import urllib.request
import json
import urllib
import pprint

PAUSE = 0.3
daily_source = "https://fuckinghomepage.com/"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'blah blah'

PARTY = False               # Bedroom LED toggle status
DETECT_TRIGGERED = False    # Motion Sensors bool
TV_TOGGLE = False           # TV on/off

def init():
    pass

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
        params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % VideoID}
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

# defines the page link, for example / is the root of the website and thus will load first. 
# adding /about or /settings will allow the users to type this is directly
@app.route("/")
def home():

    # time data
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    links = extract_daily(daily_source)

    # formatting data to be sent returned
    templateData = {
        'title' : 'mancave',
        'time': timeString,
        'article': links[0],
        'book': links[1],
        'gift': links[2],
        'website': links[3],
        'video': links[4],
        'v_title': get_video_name(links[4])
    }

    # return the html page along with the template data to be sent to client
    return render_template('index.html', **templateData)

if __name__ == "__main__":
    init()
    app.run(host='0.0.0.0', port=80, debug=True)