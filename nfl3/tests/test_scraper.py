import unittest
import urllib
from .. import scraper
from bs4 import BeautifulSoup as bs


class TestScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = scraper.Scraper()
        pass

    def test_get_json_from_page(self):
       json_data = self.scraper.get_json_from_page('Week 2', '1', '2013-2014', '9-12-2013')
       self.assertIn('2013', json_data)

    def test_get_json_select_year(self):
        json_data = self.scraper.get_json_select_year('2014-2015')
        self.assertIn('HOF', json_data)

    def test_get_line_move_urls(self):
        json_data = self.scraper.get_json_from_page('Week 2', '1', '2013-2014', '9-12-2013')
        line_move_urls = self.scraper.get_line_move_urls(json_data)
        for line in line_move_urls:
        self.assertEqual(len(line_move_urls), 16)
        self.assertTrue('http://www.covers.com/sports/odds/linehistory.aspx?eventId=37608&amp;sport=nfl' in line_move_urls)
