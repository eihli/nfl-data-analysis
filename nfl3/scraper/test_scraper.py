import unittest
import urllib
import urllib.request
import scraper
from bs4 import BeautifulSoup as bs

class TestScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = scraper.Scraper()

    def test_get_data_for_week(self):
       json_data = self.scraper.get_data_for_week('Week 2', '1', '2013-2014', '9-12-2013')
       self.assertIn('2013', json_data)

    def test_get_data_for_year(self):
        json_data = self.scraper.get_data_for_year('2014-2015')
        self.assertIn('HOF', json_data)

    def test_parse_weeks_from_data(self):
        data = self.scraper.get_data_for_year('2014-2015')
        weeks = self.scraper.parse_weeks_from_data(data)
        self.assertTrue(len(weeks) < 50)
        self.assertEqual(weeks[0]['LeagueID'], '1')

    def test_parse_years_from_data(self):
        data = self.scraper.get_data_for_year('2014-2015')
        data = self.scraper.parse_years_from_data(data)
        self.assertEqual(len(data), 8)
        self.assertIn('2012-2013', data)

    def test_parse_line_move_urls_from_data(self):
        json_data = self.scraper.get_data_for_week('Week 2', '1', '2013-2014', '9-12-2013')
        line_move_urls = self.scraper.parse_line_move_urls_from_data(json_data)
        self.assertEqual(len(line_move_urls), 16)
        self.assertTrue('http://www.covers.com/sports/odds/linehistory.aspx?eventId=37608&amp;sport=nfl' in line_move_urls)

    def test_get_list_of_year_POST_requests(self):
        l_POST_requests = self.scraper.get_list_of_year_POST_requests()
        req = l_POST_requests[0]
        f = urllib.request.urlopen(req)
        html = f.read()
        self.assertTrue(len(html) > 2000)
        self.assertIn('league', l_POST_requests[2].data.decode('utf-8'))

    def test_get_list_of_week_POST_requests(self):
        year_data = self.scraper.get_data_for_year('2014-2015')
        l_POST_requests = self.scraper.get_list_of_week_POST_requests(year_data)
        req = l_POST_requests[0]
        f = urllib.request.urlopen(req)
        html = f.read().decode('utf-8')
        self.assertIn('Line Moves', html)
        self.assertTrue(len(html) > 2000)
        self.assertIn('LeagueID', l_POST_requests[2].data.decode('utf-8'))

    def test_get_list_of_line_move_links(self):
        l_line_move_links = self.scraper.get_list_of_line_move_links()
        self.assertTrue(len(l_line_move_links) > 40)
        self.fail("Add better testing")
