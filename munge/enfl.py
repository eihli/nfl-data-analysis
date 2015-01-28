import datetime
import numpy as np
import pandas as pd

def get_prev_games(str_team_name, i_num_games, df_data, dt_start = datetime.date.today()):
    '''Return a dataframe with the number of games a team has played since today (or the provided date)

    Keyword arguments:
    str_team_name
    i_num_games
    df_data -- 'Date' column must already be pd.datetime objects
    dt_start

   
    '''
    df_data.sort('Date', ascending=False, inplace=True)

    return df_data[(df_data['TeamName'] == str_team_name) & (df_data['Date'] < dt_start)].head(i_num_games)

def get_running_league_avg(str_statname, i_num_games, df_data, dt_start = datetime.date.today()):
    '''Return the league average of given statname over the previous given number of games

    Keyword arguments:
    self-explanatory
    '''

    df_gamelist = pd.DataFrame()
    g = df_data.groupby('TeamName')
    for name, group in g:
        df_gamelist = pd.concat([df_gamelist, get_prev_games(name, i_num_games, df_data, dt_start)])

    return df_gamelist[str_statname].mean()

def map_features(X, degree = 2):
    m = len(X.columns)
    n = len(X)
    out = X.copy()
    for i in range(m):
        for j in range(i, m):
            r = pd.DataFrame({X.columns[i] + X.columns[j]: (X.iloc[:,i] * X.iloc[:,j]) })
            out = out.join(r)
    return out

def get_streaks(df, group_col, streak_col):
    streak = 0
    g = df.groupby(group_col)
    for name, group in g:
        
        for i in range(len(group)):

            while (group.ix[i, group_col] == 1):
                streak = streak + 1
                group.shift(1)
                group.ix[i+streak, groupcol] = streak

            group.shift(-streak)


def get_games_after_4_game_win_streak(df):
    g = df.groupby('TeamName')
    new_df = df.copy()
    new_df['GamesAfter4Streak'] = np.zeros(len(new_df))
    for name, group in g:
        streak_index = group[group['WinStreak'] == 4].index
        group = group.shift(-1)
        group.loc[streak_index, 'GamesAfter4Streak'] = 1
        group = group.shift(1)
        new_df[new_df['TeamName'] == name] = group

    new_df['GamesAfter4Streak'].fillna(0, inplace=True)

    return new_df

def get_adjusted_yds_off(df_data):
    df = df_data.copy()
    g1 = df.groupby('Date')
    for date, games in g1:
        g2 = games.groupby('TeamName')
        for name, game in g2:
            totalYdsOff = game['TotalYdsOff'].values[0]
            adjuster = df[(df['Date'] == date) & (df['Opponent'] == name)]['TotalYdsOffAdjuster']
            adj = (totalYdsOff + adjuster).values[0]
            df.loc[(df['Date'] == date) & (df['TeamName'] == name), 'AdjTotalYdsOff'] =  adj

    return df

def compute_cost(X, y, theta):
    predictions = X.dot(theta)
    f_sq_errors = (predictions - y) ** 2
    J = (1 / (2*m)) * f_sq_errors.sum()
    return J

def gradient_descent(X, y, theta, alpha, num_iters):
    m = y.size
    J_history = np.zeros(num_iters)
    for i in range(num_iters):
        predictions = X.dot(theta)
        theta = theta + alpha * (1/m) * X.T.dot(y - predictions)
        J_history[i] = compute_cost(X, y, theta)
    return theta, J_history

def get_running_avg(df, group_name, col_name, num):
    new_df = df.copy()
    new_df['Running' + col_name + str(num) + 'Avg'] = 0
    g = df.groupby(group_name)
    for name, group in g:
        group['Running' + col_name + str(num) + 'Avg'] = pd.rolling_mean(group[col_name], num).shift(1)
        new_df[new_df[group_name] == name] = group
    return new_df

def get_std_name(str_name):
    teams = {'ARI': ['Arizona', 'Cardinals', 'Arizona Cardinals', 'ARI', 'Phoenix, AZ'],
            'ATL': ['Atlanta', 'Falcons', 'Atlanta Falcons', 'ATL', 'Atlanta, GA', 'GA'],
            'BAL': ['Baltimore', 'Ravens', 'Baltimore Ravens', 'Baltimore, MD'],
            'BUF': ['Buffalo', 'Bills', 'Buffalo Bills', 'Buffalo, NY'],
            'CAR': ['Carolina', 'Panthers', 'Carolina Panthers', 'Charlotte, NC'],
            'CHI': ['Chicago', 'Bears', 'Chicago Bears', 'Chicago, IL'],
            'CIN': ['Cincinati', 'Bengals', 'Cincinati Bengals', 'Cincinnati', 'Cincinnati Bengals',
                    'Cincinnati, OH', 'Cincinnati OH'],
            'CLE': ['Cleveland', 'Browns', 'Cleveland Browns', 'Cleveland, OH'],
            'DAL': ['Dallas', 'Cowboys', 'Dallas Cowboys', 'Dallas, TX'],
            'DEN': ['Denver', 'Broncos', 'Denver Broncos', 'Denver, CO'],
            'DET': ['Detroit', 'Lions', 'Detroit Lions', 'Detroit, MI'],
            'GB': ['Green Bay', 'Packers', 'Green Bay Packers', 'Green Bay, WI', 'GreenBay'],
            'HOU': ['Houston', 'Texans', 'Houston Texans', 'Houston, TX'],
            'IND': ['Indianapolis', 'Colts', 'Indianapolis Colts', 'Indianapolis, IN'],
            'JAX': ['Jacksonville', 'Jaguars', 'Jacksonville Jaguars', 'Jacksonville, FL'],
            'KC': ['Kansas City', 'Chiefs', 'Kansas City Chiefs', 'Kansas City, MO', 'KansasCity'],
            'MIA': ['Miami', 'Dolphins', 'Miami Dolphins', 'Miami, FL'],
            'MIN': ['Minnesota', 'Vikings', 'Minnesota Vikings', 'Minneapolis, MN'],
            'NE': ['New England', 'Patriots', 'New England Patriots', 'Foxboro, MA', 'NewEngland'],
            'NO': ['New Orleans', 'Saints', 'New Orleans Saints', 'New Orleans, LA', 'NewOrleans'],
            'NYG': ['New York', 'Giants', 'New York Giants', 'New York, NY', 'N.Y.Giants'],
            'NYJ': ['New York', 'Jets', 'New York Jets', 'N.Y.Jets'],
            'OAK': ['Oakland', 'Raiders', 'Oakland Raiders', 'Oakland, CA'],
            'PHI': ['Philadelphia', 'Eagles', 'Philadelphia Eagles', 'Philadelphia, PA'],
            'PIT': ['Pittsburgh', 'Steelers', 'Pittsburgh Steelers', 'Pittsburgh, PA'],
            'SD': ['San Diego', 'Chargers', 'San Diego Chargers', 'San Diego, CA', 'SanDiego'],
            'SEA': ['Seattle', 'Seahawks', 'Seattle Seahawks', 'Seattle, WA', 'Seattle, Washington'],
            'SF': ['San Francisco', '49ers', 'San Francisco 49ers', 'San Francisco, CA', 'SanFrancisco'],
            'STL': ['St. Louis', 'Rams', 'St. Louis Rams', 'St Louis Rams', 'St. Louis, MO', 'St.Louis'],
            'TB': ['Tampa Bay', 'Buccaneers', 'Tampa Bay Buccaneers', 'Tampa, FL', 'TampaBay'],
            'TEN': ['Tennessee', 'Titans', 'Tennessee Titans', 'Nashville, TN'],
            'WAS': ['Washington', 'Redskins', 'Washington Redskins', 'Washington, D.C.']
            }
    for key, value in teams.items():
        for teamname in value:
            if str_name in teamname:
                return key
    return 'UNK' + str_name

def get_stadium_city(str_team):
    d_teams_stadiums = {
        'ARI':	'Phoenix, AZ',
        'ATL':	'Atlanta, GA',
        'BAL':	'Baltimore, MD',
        'BUF':	'Buffalo, NY',
        'CAR':	'Charlotte, NC',
        'CHI':	'Chicago, IL',
        'CIN':	'Cincinnati OH',
        'CLE':	'Cleveland, OH',
        'DAL':	'Dallas, TX',
        'DEN':	'Denver, CO',
        'DET':	'Detroit, MI',
        'GB':	'Green Bay, WI',
        'HOU':	'Houston, TX',
        'IND':	'Indianapolis, IN',
        'JAX':	'Jacksonville, FL',
        'KC':	'Kansas City, MO',
        'MIA':	'Miami, FL',
        'MIN':	'Minneapolis, MN',
        'NE':	'Foxboro, MA',
        'NO':	'New Orleans, LA',
        'NYG':	'New York, NY',
        'NYJ':	'New York, NY',
        'OAK':	'Oakland, CA',
        'PHI':	'Philadelphia, PA',
        'PIT':	'Pittsburgh, PA',
        'SD':	'St. Louis, MO',
        'SEA':	'San Diego, CA',
        'SF':	'San Francisco, CA',
        'STL':	'Seattle, WA',
        'TB':	'Tampa, FL',
        'TEN':	'Nashville, TN',
        'WAS':	'Washington, D.C.',}
    return d_teams_stadiums[str_team]
