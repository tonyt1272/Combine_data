import pandas as pd
import seaborn as sns
from helpers.get_data import get_data
# from Space.space import data_path
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from sklearn.preprocessing import scale

# Formatting for pandas
desired_width = 325
pd.set_option('display.width', desired_width)
pd.set_option('max_colwidth', 70)
# pd.set_option('display.colheader_justify', 'left')
pd.set_option('display.max_columns', 16)
sns.set_style('whitegrid')  # 'darkgrid'  grid lines with dark background
#                            # 'white' white background
#                            # 'ticks' ticks on side
#                            # 'whitegrid' grid lines with light background

# min_games = 40


def next_group(df_g):
    """
    For convenience when viewing dataFrame results in console.  Generates next 50 rows.
    :return: next 50 rows of the dataFrame when next() is called
    """
    start = 51
    while True:
        stop = start + 49
        yield df_g.loc[start:stop]
        start = stop + 1


def desc_size(df_40):
    if df_40['40 yard'] < 4.47:
        return 'fast'
    elif (df_40['40 yard'] >= 4.47) and (df_40['40 yard'] <= 4.57):
        return 'medium'
    else:
        return 'slow'


def target_value_db(df_t, cb_slow, cb_medium, cb_fast, min_games):
    if df_t['Name'] in cb_slow and df_t['Games'] >= min_games:
        return 'slow'
    elif df_t['Name'] in cb_medium and df_t['Games'] >= min_games:
        return 'medium'
    elif df_t['Name'] in cb_fast and df_t['Games'] >= min_games:
        return 'fast'
    else:
        return 'unsuccessful'


def target_binary(df_bin, min_games):
    if df_bin['Games'] >= min_games:
        return 1
    else:
        return 0


def impute_40(df_40, position_df):
    if pd.isna(df_40['40 yard']) and (df_40['Draft Pos'] > 32 or pd.isna(df_40['Draft Pos'])):
        return position_df['40 yard'].mean() + position_df['40 yard'].std()*.5
    elif pd.isna(df_40['40 yard']) and df_40['Draft Pos'] <= 32:
        return position_df['40 yard'].mean()
    else:
        return df_40['40 yard']


def impute_vert(df_v, position_df):
    if pd.isna(df_v['Vert leap']) and (df_v['Draft Pos'] > 32 or pd.isna(df_v['Draft Pos'])):
        return position_df['Vert leap'].mean() - position_df['Vert leap'].std()*.5
    elif pd.isna(df_v['Vert leap']) and df_v['Draft Pos'] <= 32:
        return position_df['Vert leap'].mean()
    else:
        return df_v['Vert leap']


def impute_bench(df_b, position_df):
    if pd.isna(df_b['Bench press']) and (df_b['Draft Pos'] > 32 or pd.isna(df_b['Draft Pos'])):
        return position_df['Bench press'].mean() - position_df['Bench press'].std()*.5
    elif pd.isna(df_b['Bench press']) and df_b['Draft Pos'] <= 32:
        return position_df['Bench press'].mean()
    else:
        return df_b['Bench press']


def impute_bj(df_bj, position_df):
    if pd.isna(df_bj['Broad jump']) and (df_bj['Draft Pos'] > 32 or pd.isna(df_bj['Draft Pos'])):
        return position_df['Broad jump'].mean() - position_df['Broad jump'].std()*.5
    elif pd.isna(df_bj['Broad jump']) and df_bj['Draft Pos'] <= 32:
        return position_df['Broad jump'].mean()
    else:
        return df_bj['Broad jump']


def impute_shuttle(df_s, position_df):
    if pd.isna(df_s['Shuttle']) and (df_s['Draft Pos'] > 32 or pd.isna(df_s['Draft Pos'])):
        return position_df['Shuttle'].mean() + position_df['Shuttle'].std()*.5
    elif pd.isna(df_s['Shuttle']) and df_s['Draft Pos'] <= 32:
        return position_df['Shuttle'].mean()
    else:
        return df_s['Shuttle']


def get_corners(year_start=1987, year_stop=2020, min_games=40):
    years_corners = range(year_start, year_stop+1)
    corner_columns = ['Name', 'Height(in)', 'Weight(lbs)', '40 yard', 'Bench press', 'Vert leap', 'Broad jump',
                      'Shuttle', 'HOF', 'College_x', 'College_y', 'Draft Pos', 'Games', 'Draft Year', 'POS']

    corners_all_years = pd.DataFrame(columns=corner_columns)    # initializing corners dataframe

    for year in years_corners:
        df = get_data(year, to_file=False)  # get combine and draft position (if drafted) and games in NFL, one year
        # positions = df['POS_x'].unique()
        df['POS'] = df['POS_x'].copy()
        df.drop(['POS_x', 'POS_y', 'url'], axis=1, inplace=True)

        df_corners = df[(df['POS'] == 'SS') | (df['POS'] == 'FS') | (df['POS'] == 'CB')][:]
        # df_corners = df[df['POS'] == 'CB'].copy()

        df_corners['Draft Year'] = year

        corners_all_years = corners_all_years.append(df_corners)

    corners_all_years['Bench press'] = corners_all_years.apply(impute_bench, position_df=corners_all_years, axis=1)
    corners_all_years['Vert leap'] = corners_all_years.apply(impute_vert, position_df=corners_all_years, axis=1)
    corners_all_years['Broad jump'] = corners_all_years.apply(impute_bj, position_df=corners_all_years, axis=1)
    corners_all_years['Shuttle'] = corners_all_years.apply(impute_shuttle, position_df=corners_all_years, axis=1)
    corners_all_years['40 yard'] = corners_all_years.apply(impute_40, position_df=corners_all_years, axis=1)
    corners_all_years.reset_index(inplace=True, drop=True)

    # corners_all_years.to_csv(data_path('Combine_by_position_all_years/corners_all_years.csv'), index=True)

    # ### KMeans CLuster and Plot ####

    kmeans = KMeans(n_clusters=3)
    df_features = corners_all_years[['Name', '40 yard', 'Height(in)', 'Weight(lbs)', 'Bench press', 'Shuttle',
                                     'Broad jump', 'Vert leap', 'Games']]
    df_features['Games'].fillna(0, inplace=True)

    df_features = df_features[df_features['Games'] >= min_games].copy()
    df_features.reset_index(drop=True)

    # ### For cluster and plot ###
    df_fit = df_features[['Name', '40 yard', 'Height(in)', 'Weight(lbs)', 'Games']].dropna()
    kmeans.fit(df_fit[['40 yard']].values)
    x = df_fit['40 yard']
    y = df_fit['Games']
    fig = plt.figure(1, figsize=(10, 6))
    ax1 = fig.add_axes([.1, .1, .8, .8])
    min_max_scaler = MinMaxScaler()
    size = df_fit['Height(in)']  # for size of circles in cluster plot
    size_norm = min_max_scaler.fit_transform(size.values.reshape(-1, 1))  # normalizing the size
    ax1.scatter(x, y, c=kmeans.labels_, s=size_norm * 150, alpha=.3, cmap='brg', facecolors='none')
    # ### END Plotting ###

    # ### Create Speed  Labels ###
    df_fit['labels'] = kmeans.labels_
    df_fit['speed'] = df_fit.apply(desc_size, axis=1)

    df_fast = df_fit[df_fit['speed'] == 'fast']
    df_medium = df_fit[df_fit['speed'] == 'medium']
    df_slow = df_fit[df_fit['speed'] == 'slow']

    cb_fast = list(df_fast['Name'].values)
    cb_medium = list(df_medium['Name'].values)
    cb_slow = list(df_slow['Name'].values)
    # ######

    corners_all_years['target'] = corners_all_years.apply(target_value_db, cb_slow=cb_slow, cb_medium=cb_medium,
                                                          cb_fast=cb_fast, min_games=min_games, axis=1)

    # corners_all_years['target'] = corners_all_years.apply(target_binary, min_games=min_games, axis=1)

    corners_target = corners_all_years[corners_all_years['40 yard'].notna()][:]
    corners_target['Weight(lbs)'] = pd.to_numeric(corners_target['Weight(lbs)'])

    corners_data = corners_target.drop(['College_x', 'College_y', 'POS'], axis=1)[:]

    corners_data['HOF'] = corners_data['HOF'].fillna(0)
    corners_data['Games'] = corners_data['Games'].fillna(0)
    corners_data.reset_index(drop=True, inplace=True)

    # ### Shuffle the data ###
    shuffle_index = np.arange(0, len(corners_data))
    np.random.shuffle(shuffle_index)
    corners_data['shuffle_index'] = shuffle_index
    corners_data.sort_values('shuffle_index', inplace=True)
    corners_data.reset_index(drop=True, inplace=True)
    corners_data.drop('shuffle_index', axis=1, inplace=True)

    corners_data['target'] = corners_data['target'].astype('category')[:]
    corners_data['Bench press'] = corners_data['Bench press'].astype('int')[:]
    # corners_data['Draft Pos'] = corners_data['Draft Pos'].astype('int')[:]
    corners_data['Games'] = corners_data['Games'].astype('int')[:]
    # corners_data['Draft Year'] = corners_data['Draft Year'].astype('int')[:]
    # ###

    # features_final = corners_data[['Height(in)', 'Weight(lbs)', '40 yard', 'Bench press', 'Vert leap', 'Broad jump',
    #                                'Shuttle']][:]

    features_final = corners_data[['Height(in)', 'Weight(lbs)', '40 yard', 'Bench press', 'Vert leap', 'Shuttle']][:]

    # features_final = corners_data[['Height(in)', 'Weight(lbs)', '40 yard', 'Bench press', 'Shuttle']][:]

    # features_final = corners_data[['Height(in)', 'Weight(lbs)', '40 yard', 'Bench press', 'Vert leap']][:]

    # features_final = corners_data[['Height(in)', 'Weight(lbs)', '40 yard', 'Bench press']][:]

    # features_final = corners_data[['Height(in)', 'Weight(lbs)', '40 yard', 'Shuttle','Vert leap']][:]

    # features_final = corners_data[['Height(in)', 'Weight(lbs)', '40 yard', 'Shuttle']][:]

    df = features_final[:]
    try:
        df['Height(in)'] = scale(df['Height(in)'])      # "Center the mean and component wise scale to unit variance."
    except KeyError:
        pass
    try:
        df['Weight(lbs)'] = scale(df['Weight(lbs)'])
    except KeyError:
        pass
    try:
        df['40 yard'] = scale(df['40 yard'])
    except KeyError:
        pass

    try:
        df['Bench press'] = scale(df['Bench press'])
    except KeyError:
        pass

    try:
        df['Vert leap'] = scale(df['Vert leap'])
    except KeyError:
        pass

    try:
        df['Broad jump'] = scale(df['Broad jump'])
    except KeyError:
        pass

    try:
        df['Shuttle'] = scale(df['Shuttle'])
    except KeyError:
        pass

    """
    Notes:
    1.  Broad jump appears to be mostly noise, makes predictions worse when included.
    2.  
    """
    targets_final = corners_data[['target']][:]

    features_final = df.copy()

    return corners_data, features_final, targets_final


if __name__ == '__main__':
    corners_data_, features_final_, targets_final_ = get_corners(1987, 2017, min_games=40)
