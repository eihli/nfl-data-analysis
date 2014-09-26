import unittest
import urllib
import scraper
from bs4 import BeautifulSoup as bs


class TestScraper(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_json_from_page(self):
       self.scrape = scraper.Scraper()
       json_data = self.scrape.get_json_from_page('Week 2', '1', '2013-2014', '9-12-2013')
       self.assertIn('2013', json_data)
