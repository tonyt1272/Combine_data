import pandas as pd
import seaborn as sns
from helpers.get_data import get_data
# from Space.space import data_path
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import numpy as np

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

min_games = 40


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


def target_value(df_t):
    if df_t['Name'] in cb_slow and df_t['Games'] >= min_games:
        return 'slow'
    elif df_t['Name'] in cb_medium and df_t['Games'] >= min_games:
        return 'medium'
    elif df_t['Name'] in cb_fast and df_t['Games'] >= min_games:
        return 'fast'
    else:
        return 'unsuccessfull'


def impute_vert(df_v):
    if pd.isna(df_v['Vert leap']) and (df_v['Draft Pos'] > 32 or pd.isna(df_v['Draft Pos'])):
        return corners_all_years['Vert leap'].mean() - corners_all_years['Vert leap'].std()*.5
    elif pd.isna(df_v['Vert leap']) and df_v['Draft Pos'] <= 32:
        return corners_all_years['Vert leap'].mean()
    else:
        return df_v['Vert leap']


def impute_bench(df_b):
    if pd.isna(df_b['Bench press']) and (df_b['Draft Pos'] > 32 or pd.isna(df_b['Draft Pos'])):
        return corners_all_years['Bench press'].mean() - corners_all_years['Bench press'].std()*.5
    elif pd.isna(df_b['Bench press']) and df_b['Draft Pos'] <= 32:
        return corners_all_years['Bench press'].mean()
    else:
        return df_b['Bench press']


if __name__ == '__main__':
    years = range(1987, 2018)
    corner_columns = ['Name', 'Height(in)', 'Weight(lbs)', '40 yard', 'Bench press', 'Vert leap', 'Broad jump', 'Shuttle',
                  'HOF', 'College_x', 'College_y', 'Draft Pos', 'Games', 'Draft Year', 'POS']
    corners_all_years = pd.DataFrame(columns=corner_columns)
    for year in years:
        df = get_data(year, to_file=False)  # get combine and draft position (if drafted) and games in NFL, one year
        # positions = df['POS_x'].unique()
        df['POS'] = df['POS_x']
        df.drop(['POS_x', 'POS_y', 'url'], axis=1, inplace=True)
        # df_db = df[(df['POS'] == 'SS') | (df['POS'] == 'FS') | (df['POS'] == 'CB')]
        df_corners = df[df['POS'] == 'CB']
        df_corners['Draft Year'] = year

        corners_all_years = corners_all_years.append(df_corners).copy()

    corners_all_years['Bench press'] = corners_all_years.apply(impute_bench, axis=1)
    corners_all_years['Vert leap'] = corners_all_years.apply(impute_vert, axis=1)
    corners_all_years.reset_index(inplace=True, drop=True)
    # print(corners_all_years.info())
    # print(corners_all_years.describe())
    a = next_group(corners_all_years)
    # corners_all_years.to_csv(data_path('Combine_by_position_all_years/corners_all_years.csv'), index=True)

    kmeans = KMeans(n_clusters=3)
    df_features = corners_all_years[['Name', '40 yard', 'Height(in)', 'Weight(lbs)', 'Bench press', 'Shuttle',
                                     'Vert leap', 'Games']]
    df_features['Games'].fillna(0, inplace=True)

    df_features = df_features[df_features['Games'] >= min_games].copy()
    df_features.reset_index(drop=True)

    # ### For cluster and plot ###
    df_fit = df_features[['Name', '40 yard', 'Height(in)', 'Weight(lbs)', 'Games']].dropna()

    kmeans.fit(df_fit[['40 yard']].values)
    # kmeans.labels_

    x = df_fit['40 yard']
    y = df_fit['Games']

    fig = plt.figure(1, figsize=(10, 6))

    ax1 = fig.add_axes([.1, .1, .8, .8])

    min_max_scaler = MinMaxScaler()
    size = df_fit['Height(in)']
    size_norm = min_max_scaler.fit_transform(size.values.reshape(-1, 1))

    ax1.scatter(x, y, c=kmeans.labels_, s=size_norm * 150, alpha=.3, cmap='brg', facecolors='none')

    df_fit['labels'] = kmeans.labels_

    df_fit['speed'] = df_fit.apply(desc_size, axis=1)

    df_fast = df_fit[df_fit['speed'] == 'fast']
    df_medium = df_fit[df_fit['speed'] == 'medium']
    df_slow = df_fit[df_fit['speed'] == 'slow']

    cb_fast = list(df_fast['Name'].values)
    cb_medium = list(df_medium['Name'].values)
    cb_slow = list(df_slow['Name'].values)

    # ######

    corners_all_years['target'] = corners_all_years.apply(target_value, axis=1)
    corners_target = corners_all_years[corners_all_years['40 yard'].notna()]

    corners_target['Weight(lbs)'] = pd.to_numeric(corners_target['Weight(lbs)'])

    corners_data = corners_target.drop(['College_x', 'College_y', 'POS', 'Shuttle', 'Broad jump'],
                                       axis=1).copy()

    corners_data['HOF'] = corners_data['HOF'].fillna(0).copy()
    corners_data['Games'] = corners_data['Games'].fillna(0).copy()
    corners_data.reset_index(drop=True, inplace=True)

    print(corners_data.info())

    shuffle_index = np.arange(0, len(corners_data))
    np.random.shuffle(shuffle_index)
    corners_data['shuffle_index'] = shuffle_index
    corners_data.sort_values('shuffle_index', inplace=True)
    corners_data.set_index('shuffle_index', inplace=True)
    corners_data.reset_index(drop=True, inplace=True)
    b = next_group(corners_data)

    features_final = corners_data[['Height(in)', 'Weight(lbs)', '40 yard', 'Bench press', 'Vert leap']].copy()
    targets_final = corners_data[['target']]



