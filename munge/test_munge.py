import pandas as pd
import unittest

class TestMunge(unittest.TestCase):

    def setUp(self):
        self.data = pd.read_csv('../scrapers/covers/test2_csv.csv')

    def test_setup(self):
        print(self.data.head())
        self.assertTrue(isinstance(self.data, pd.DataFrame))

