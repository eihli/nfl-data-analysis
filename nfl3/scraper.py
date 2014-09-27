import urllib
import re
import json
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup as bs

class Scraper():
    
    def __init__(self):

        self.select_week_url = "http://scores.covers.com/ajax/SportsDirect.Controls.LiveScoresControls.Scoreboard,SportsDirect.Controls.LiveScoresControls.ashx?_method=UpdateScoreboard&_session=no"
        self.select_year_url= "http://scores.covers.com/ajax/SportsDirect.Controls.LiveScoresControls.ScoresCalendar,SportsDirect.Controls.LiveScoresControls.ashx?_method=changeDay&_session=no"

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
        f = urllib.request.urlopen(self.select_week_url, data)
        json_data = f.read().decode('utf-8')
        return json_data
    
    def get_json_select_year(self, season_string):
        data = {
                'league': '1',
                'SeasonString': season_string,
                'Year': '1',
                'Month': '1',
                'Day': '1'
        }
        data = urllib.parse.urlencode(data).replace('&', '\n').encode('utf-8')
        f = urllib.request.urlopen(self.select_year_url, data)
        json_data = f.read().decode('utf-8')
        return json_data
    
    def get_years_from_text(self, text):
        p = re.compile(r'<option value="(\d{4,4}-\d{4,4})"')
        years = p.findall(text)
        return years

    def get_line_move_urls(self, data):
        p = re.compile(r'<a href="(http://www\.covers\.com/sports/odds/linehistory\.aspx.*?)".*?Line Moves')
        urls = p.findall(data)
        return urls

    def get_list_of_weeks(self, data):
        re.purge()
        p = re.compile(r'<option value="(.{1,40}?)">(\D.{1,20})</option>')
        list_of_weeks = p.findall(data)
        l_weeks = []
        for data, week in list_of_weeks:
            data = data.rsplit(',')
            league = data[0]
            season = data[1]
            gamedate = data[3] + '-' + data[4] + '-' + data[2]
            l_weeks.append({'LeagueID': league,
                'SeasonString': season,
                'GameDate': gamedate,
                'Week': week
                })
        return l_weeks
