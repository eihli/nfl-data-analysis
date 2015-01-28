import re
import datetime
import os
import shelve
import unittest
import urllib.request
import covers_scraper

class TestScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = covers_scraper.Scraper()
        self.d = shelve.open('line_movement_shelf')
        self.f = open('new_line_move_links.txt')
        self.link_list = [link.strip() for link in self.f]
        self.f.close()
        self.test_html = self.d[self.link_list[0]].decode('utf-8').\
                replace('\n', '').replace('\r', '').replace('\t', '')
        self.test_html_no_line_history = self.d[self.link_list[1350]].\
                decode('utf-8').replace('\n', '').replace('\r', '').\
                replace('\t', '')

    def tearDown(self):
        self.d.close()

    def test_get_data_for_week(self):
       html = self.scraper.get_data_for_week('Week 2', '1', '2013-2014', '9-12-2013')
       self.assertIn('2013', html)

    def test_get_data_for_year(self):
        html = self.scraper.get_data_for_year('2014-2015')
        self.assertIn('HOF', html)

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
        html = self.scraper.get_data_for_week('Week 2', '1', '2013-2014', '9-12-2013')
        line_move_urls = self.scraper.parse_line_move_urls_from_data(html)
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
        result = covers_scraper.Scraper.parse_line_movement_gamedate(html)
        self.assertEqual(result.hour, datetime.time(hour=20).hour)

    def test_parse_line_movement_teams(self):
        html = self.d[self.link_list[0]].decode('utf-8')
        result = covers_scraper.Scraper.parse_line_movement_teams(html)
        self.assertEqual(result[0], 'Miami')
        self.assertEqual(result[1], 'Dallas')

    def test_parse_line_movement_sportsbooks(self):
        result = covers_scraper.Scraper.parse_line_movement_sportsbooks(self.\
                test_html)
        self.assertTrue(any('5Dimes.eu' in i for i in result))
        self.assertTrue('07/25/13' in result['5Dimes.eu'])

    def test_parse_movement_datetime(self):

        result = covers_scraper.Scraper.parse_movement_datetime(self.\
                test_html)
        self.assertTrue(result['5Dimes.eu'][0].hour == 9)

    def test_parse_line_movements(self):

        str_test_eventid = '37575'
        dt_test_gamedate = datetime.datetime(2013,8,4,20)
        dt_test_movement = datetime.datetime(2013, 8, 4, 19, 21, 23)
        str_test_home_team = 'Dallas'
        str_test_away_team = 'Miami'
        str_test_bookname = 'GTBets.eu'
        str_test_pointspread = '3'
        str_test_overunder = '33'
        str_test_pointspread_price = '-110'
        str_test_overunder_price = '-110'

        result = covers_scraper.Scraper.parse_line_movements(self.test_html)
        self.assertEqual(result[0][0], '37575')
        self.assertEqual(result[0][2], 'Dallas')
        self.assertTrue((str_test_eventid, dt_test_gamedate,
            str_test_home_team, str_test_away_team,
            str_test_bookname, dt_test_movement,
            str_test_pointspread, str_test_pointspread_price, 
            str_test_overunder, str_test_overunder_price) in result)

        result = covers_scraper.Scraper.parse_line_movements(self.test_html_no_line_history)
        self.assertEqual(result, None)

    def test_save_line_movements_to_csv(self):

        filename = 'test_csv_line_movements.csv'
        result = covers_scraper.Scraper.save_line_movements_to_csv([self.test_html], filename)
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
