import urllib.request
import json
import urllib.parse

class Scraper():

    def __init__(self):
        pass

    def scrape(self):
        url = 'http://scores.covers.com/ajax/SportsDirect.Controls.LiveScoresControls.ScoresCalendar,SportsDirect.Controls.LiveScoresControls.ashx?_method=changeDay&_session=no'

        data = {
            'league': '1',
            'SeasonString': '2012-2013',
            'Year': '1',
            'Month': '1',
            'Day': '1'
        }        

        data = urllib.parse.urlencode(data)

        headers = {
            'Host': 'scores.covers.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://scores.covers.com/football-scores-matchups.aspx',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }

        req = urllib.request.Request(url)
        req.data = data
        req.headers = headers

        f = urllib.request.urlopen(req)
        print(f.read())

        return f
    
