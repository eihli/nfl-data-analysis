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

    def get_data_for_week(self, week, league, season, gamedate):
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
    
    def get_data_for_year(self, season_string):
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
    
    def parse_years_from_data(self, text):
        p = re.compile(r'<option value="(\d{4,4}-\d{4,4})"')
        years = p.findall(text)
        return years

    def parse_line_move_urls_from_data(self, data):
        p = re.compile(r'<a href="(http://www\.covers\.com/sports/odds/linehistory\.aspx.*?)".*?Line Moves')
        urls = p.findall(data)
        return urls

    def parse_weeks_from_data(self, year_data):
        p = re.compile(r'<option value="(.{1,40}?)">(\D.{1,20})</option>')
        list_of_weeks = p.findall(year_data)
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
    
    def get_list_of_year_POST_requests(self):
        start_year = '2014-2015'
        html = self.get_data_for_year(start_year)
        l_years = self.parse_years_from_data(html)
        l_requests = []
        for year in l_years:
            data = {
                    'league': '1',
                    'SeasonString': year,
                    'Year': '1',
                    'Month': '1',
                    'Day': '1'
            }
            data = urllib.parse.urlencode(data).replace('&', '\n').encode('utf-8')
            l_requests.append(urllib.request.Request(self.select_year_url, data))
        return l_requests

    def get_list_of_week_POST_requests(self, year_data):
        ld_weeks = self.parse_weeks_from_data(year_data)
        l_requests = []
        for week in ld_weeks:
            d_data = week
            if d_data['Week'] == 'HOF':
                d_data['Week'] = 'Pre-Season Hall-of-Fame Week'
            d_data['Season'] = d_data.pop('SeasonString')
            d_data['Refresh'] = 'false'
            d_data['LastUpdateTime'] = '01-01-1900'
            d_data['type'] = 'Matchups'
            d_data['RefreshStartTime'] = ''
            d_data['conferenceID'] = ''
            d_data = urllib.parse.urlencode(d_data).replace('&', '\n') \
                    .replace('+', ' ').encode('utf-8')
            l_requests.append(urllib.request.Request(self.select_week_url, d_data))
        return l_requests

    def get_list_of_line_move_links(self):
        l_line_move_urls = []
        l_year_requests = self.get_list_of_year_POST_requests()
        for year_request in l_year_requests:
            year_data = urllib.request.urlopen(year_request)\
                .read().decode('utf-8')
            l_week_requests = self.get_list_of_week_POST_requests(year_data)
            for week_request in l_week_requests:
                week_data = urllib.request.urlopen(week_request)\
                    .read().decode('utf-8')
                line_move_urls = self.parse_line_move_urls_from_data\
                    (week_data)
                l_line_move_urls += line_move_urls
        f = open('line_move_links.txt', 'w')
        for item in l_line_move_urls:
            f.write("%s\n" % item)
        f.close()


