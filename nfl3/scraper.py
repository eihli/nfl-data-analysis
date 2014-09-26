import urllib
import json
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup as bs

class Scraper():
    
    def __init__(self):
        self.base_url = "http://scores.covers.com" 
        self.ajax_url = "http://scores.covers.com/ajax/SportsDirect.Controls.LiveScoresControls.Scoreboard,SportsDirect.Controls.LiveScoresControls.ashx?_method=UpdateScoreboard&_session=no"

    def get_json_from_page(self, week, league, season, gamedate):
        str_html_year = ''
        data = {'LeagueID': league, 'GameDate': gamedate,
                'Season': season, 'Refresh': '',
                'LastUpdateTime': '01-01-1900',
                'type': 'Matchups',
                'RefreshStartTime': '',
                'Week': week,
                'conferenceID': '',
        }
        data = urllib.parse.urlencode(data).replace('&','\n').replace('+',' ').encode('utf-8')
        f = urllib.request.urlopen(self.ajax_url, data)
        json_data = f.read().decode('utf-8')
        return json_data
