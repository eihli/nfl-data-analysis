import enfl
import pandas as pd
import datetime
import shelve

class Cobra:
    def __init__(self):

        self.df_games = pd.read_csv('data/games.csv', parse_dates = [1])
        self.df_line_moves = pd.read_csv('data/line_movements.csv',
                parse_dates = [1, 5])

        self.df_line_moves['Date'] = self.df_line_moves['gamedate'].apply(lambda x: datetime.datetime.date(x))
        self.df_line_moves['home_team_key'] = self.df_line_moves['hometeam'].apply(lambda x: enfl.get_std_name(x))
        self.df_line_moves['away_team_key'] = self.df_line_moves['awayteam'].apply(lambda x: enfl.get_std_name(x))

        self.df_line_moves['line_move_date'] = self.df_line_moves['linemovementdate'].apply(lambda x: datetime.datetime.date(x))
        self.df_line_moves = self.df_line_moves[(self.df_line_moves['pointspread'] != 'OFF') & (self.df_line_moves['overunder'] != 'OFF')]
        self.df_line_moves['pointspread'] = self.df_line_moves['pointspread'].astype(float)
        self.df_line_moves['overunder'] = self.df_line_moves['overunder'].astype(float)

        g = self.df_line_moves.groupby('eventid')
        self.point_spread_open = g.apply(lambda x: x.groupby('line_move_date').apply(lambda z: z.sort('linemovementdate')['pointspread'].mean())[0])
        self.point_spread_close = g.apply(lambda x: x.groupby('line_move_date').apply(lambda z: z.sort('linemovementdate')['pointspread'].mean())[-1])


        print(self.df_games.tail())
        print(self.df_line_moves.tail())
    pass
