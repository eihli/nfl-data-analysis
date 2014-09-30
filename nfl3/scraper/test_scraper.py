import re
import datetime
import os
import shelve
import unittest
import urllib
import urllib.request
import scraper
from bs4 import BeautifulSoup as bs

class TestScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = scraper.Scraper()
        self.d = shelve.open('line_movement_shelf')
        self.f = open('new_line_move_links.txt')
        self.link_list = [link.strip() for link in self.f]
        self.f.close()
        self.test_parse_html = self.d[self.link_list[0]].decode('utf-8').\
                replace('\n', '').replace('\r', '').replace('\t', '')

    def tearDown(self):
        self.d.close()

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

    def test_parse_line_movement_html(self):
        for i in range(5):
            html = self.d[self.link_list[i]]

    def test_parse_line_movement_gamedate(self):
        html = self.d[self.link_list[0]].decode('utf-8')
        result = scraper.Scraper.parse_line_movement_game_date(html)
        self.assertEqual(result.hour, datetime.time(hour=20).hour)

    def test_parse_line_movement_teams(self):
        html = self.d[self.link_list[0]].decode('utf-8')
        result = scraper.Scraper.parse_line_movement_teams(html)
        self.assertEqual(result[0], 'Miami')
        self.assertEqual(result[1], 'Dallas')

    def test_parse_line_movement_sportsbooks(self):
        result = scraper.Scraper.parse_line_movement_sportsbooks(self.\
                test_parse_html)
        self.assertTrue(any('5Dimes.eu' in i for i in result))
        self.assertTrue('07/25/13' in result['5Dimes.eu'])

    def test_parse_movement_datetime(self):
        result = scraper.Scraper.parse_movement_datetime(self.\
                test_parse_html)
        self.assertTrue(result['5Dimes.eu'][0].hour == 9)

    def test_parse_line_movements(self):
        result = scraper.Scraper.parse_line_movements(self.test_parse_html)
        self.assertEqual(result[0][0], '37575')

    def test_save_line_movements_to_csv(self):
        filename = 'test_csv_line_movements.csv'
        result = scraper.Scraper.save_line_movements_to_csv([self.test_parse_html], filename)
        f = open(filename)
        csv = f.readlines()
        print(csv[1])
        f.close()
        self.fail('This test sucks')



#    def test_get_list_of_week_POST_requests(self):
#        year_data = self.scraper.get_data_for_year('2014-2015')
#        l_POST_requests = self.scraper.get_list_of_week_POST_requests(year_data)
#        req = l_POST_requests[0]
#        f = urllib.request.urlopen(req)
#        html = f.read().decode('utf-8')
#        self.assertIn('Line Moves', html)
#        self.assertTrue(len(html) > 2000)
#        self.assertIn('LeagueID', l_POST_requests[2].data.decode('utf-8'))

#    def test_get_list_of_line_move_links(self):
#        l_line_move_links = self.scraper.get_list_of_line_move_links()
#        self.assertTrue(len(l_line_move_links) > 40)

#    def test_get_and_shelve_line_movement_html(self):
#        link_list = ['http://www.covers.com/sports/odds/linehistory.aspx?eventId=37575&sport=nfl']
#        shelf = shelve.open('line_movements_shelf', 'r')
#        self.scraper.get_and_shelve_line_movement_html(link_list, shelf)
#        self.assertTrue(os.path.isfile('line_movements_shelf.dat'))
#        test_html = """
#    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
#    <HTML>
#        <HEAD>
#            
#
#    <!-- Start Meta Data -->
#    <meta http-equiv="X-UA-Compatible" value="IE=9">
#    <TITLE>NFL Line History - Football Betting Odds</TITLE>
#    <meta http-equiv="Content-Type" content="text/html; charset=windows-1252">
#"""
#        test_html = "".join(test_html.split())
#        self.assertIn(test_html, "".join(shelf[link_list[0]].decode('utf-8').split()))
#        shelf.close()
#        self.fail("You just made sure things were writing to the shelf. Now try writing multiple pages to the shelf. Once you get multiple pages writing and retrieving from shelf, run it on all the links in the list")
