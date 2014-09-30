import urllib
import datetime
import shelve
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
    
    def parse_line_movement_gamedate(html):
        p = re.compile(r'h3LineHistory"><div class="right">(.*?)</div>', re.S)
        result = p.search(html).group(1)
        p = re.compile(r' ([0-9]):')
        hour = p.search(result)
        if hour.end(1) - hour.start(1) > 1:
            result = result[:hour.start()+1] + 0 + result[hour.end():] 
        result = datetime.datetime.strptime(result, '%a, %B %d/%y %I:%M %p ET')
        return result

    def parse_line_movement_teams(html):
        html = ''.join((html.replace('\n', '').replace('\r','')).split())
        p = re.compile(r'h3LineHistory.*?</div>(.*?)vs.(.*?)</h3>')
        result = p.search(html)
        result = [result.group(1), result.group(2)]
        return result
    
    def parse_line_movement_sportsbooks(html):
        p = re.compile(r'#ECECE4.*?underline;">(.*?)</a>(.*?)(#ECECE4|</table>)')
        result = p.findall(html)
        result = dict((key, value) for key, value, what in result)
        return result

    def parse_movement_datetime(html):
        p = re.compile(r'<tr.*?<td.*?>(\d.*?)<')
        p1 = re.compile(r' (\d):')
        sportsbooks = Scraper.parse_line_movement_sportsbooks(html)
        d_lines = {}
        for book in sportsbooks:
            d_lines[book] = []
            results = p.findall(sportsbooks[book])
            for line in results:
                match = p1.search(line)
                # Convert 1 digit hours to 2 digit hours
                if match:
                    line = line[:match.start() + 1] + '0' + line[match.end()-2:]
                    
                line = datetime.datetime.strptime(line, '%m/%d/%y %I:%M:%S %p')
                d_lines[book].append(line)
        return d_lines

    def parse_point_spread(html):

        p = re.compile(r'<tr bgcolor="#FFFFFF">(<td.*?</td>)' + \
                '(<td.*?</td>)(<td.*?</td>)</tr>')
        results = p.findall(html)
        p = re.compile(r'((-\d*?)|(\d*?))/|>(([A-Z])*?<)')

        for line in results:
            point_spread = p.search(line[1]).group(1)
    
    def parse_line_movements(html):

        date = Scraper.parse_line_movement_gamedate(html)
        home_team, away_team = Scraper.parse_line_movement_teams(html)

        re_table = re.compile(r'<table id="ucLineHistory_tblLineHistory".*?</table>')
        
        table = re_table.search(html).group(0)

        re_sportsbooks = re.compile(r'<td class="smtext2" width="40%">(.*?)(tr bgcolor="#ECECE4">|</table>)')
        re_sportsbook_name = re.compile(r'Covers Line History".*?>(.*?)<')

        sportsbook_names = re_sportsbook_name.findall(table)
        sportsbooks_table = re_sportsbooks.findall(table)
        d_sportsbooks = dict(zip(sportsbook_names, sportsbooks_table))

        re_line_movement = re.compile(r"""
            <tr\ bgcolor="\#FFFFFF"> # Row...
            .*?>(.*?)</td>           # First column
            .*?>(.*?)</td>           # Second column
            .*?>(.*?)</td>           # Third columnd
            """, re.X)
        re_hour_digit = re.compile(r' (\d*?):')
        re_point_spread = re.compile(r'(.*?)/')
        re_over_under_half_point = re.compile(r'..\..')
        re_over_under = re.compile(r'..')

        l_result = []
        
        for bookname in d_sportsbooks.keys():
            print(bookname)

            # The values in sportsbooks are tuples because it's the only way
            # you could get regex to work. value in [0] index is the
            # one you want
            l_line_movements = re_line_movement.findall(d_sportsbooks[bookname][0])

            for line_movement in l_line_movements:

                # Format the datetime
                dt_line_movement = line_movement[0]
                hour = re_hour_digit.search(dt_line_movement)
                if len(hour.group(1)) == 1:
                    dt_line_movement = dt_line_movement[:hour.start() + 1]\
                          + '0' + dt_line_movement[hour.end() - 2:]
                dt_line_movement = datetime.datetime.strptime(dt_line_movement,
                        '%m/%d/%y %I:%M:%S %p')

                # Parse and format the point spread
                point_spread = line_movement[1]
                point_spread = re_point_spread.search(point_spread)
                if not point_spread:
                    point_spread = 'OFF'
                else:
                    point_spread = point_spread.group(1)
                
                # TODO: Parse and format point spread ODDS

                # Parse and format Over Under
                over_under = line_movement[2]
                if re_over_under_half_point.search(over_under):
                    over_under = re_over_under_half_point.search(over_under)
                else:
                    over_under = re_over_under.search(over_under)
                over_under = over_under.group(0)

                l_result.append((bookname, dt_line_movement, point_spread,
                    over_under))
        print(len(l_result))
        return l_result


#    def get_list_of_line_move_links(self):
#        l_line_move_urls = []
#        l_year_requests = self.get_list_of_year_POST_requests()
#        for year_request in l_year_requests:
#            year_data = urllib.request.urlopen(year_request)\
#                .read().decode('utf-8')
#            l_week_requests = self.get_list_of_week_POST_requests(year_data)
#            for week_request in l_week_requests:
#                week_data = urllib.request.urlopen(week_request)\
#                    .read().decode('utf-8')
#                line_move_urls = self.parse_line_move_urls_from_data\
#                    (week_data)
#                l_line_move_urls += line_move_urls
#        f = open('line_move_links.txt', 'w')
#        for item in l_line_move_urls:
#            f.write("%s\n" % item)
#        f.close()

#    def get_and_shelve_line_movement_html(self, link_list, shelf):
#        for link in link_list:
#            key = link
#            value = urllib.request.urlopen(link).read()
#            shelf[key] = value
#        return

