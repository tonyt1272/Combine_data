import pandas as pd
import seaborn as sns
from helpers.get_data import get_data, get_combine

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


def next_group(df):
    """
    For convenience when viewing dataFrame results in console.  Generates next 50 rows.
    :return: next 50 rows of the dataFrame when next() is called
    """
    start = 51
    while True:
        stop = start + 49
        yield df.loc[start:stop]
        start = stop + 1


if __name__ == '__main__':
    # df = get_combine(1988, to_file=False)   # get just the combine data, one year
    # print(df.loc[0:50])
    # a = next_group(df)
    # next(a)  # returns the next 50 player's combine results
    #
    # for year in range(1987, 2021):    # get all years at once
    #     get_combine(year, to_file=True)
    #     print(f'{year} saved successfully')

    # ###
    year = 1991
    df = get_data(year, to_file=False)  # get combine and draft position (if drafted) and games in NFL, just one year

    a = next_group(df)
    # next(a)  # returns the next 50 player's combine results

    # for year in range(1987, 2021):    # get all years at once
    #     df = get_data(year, to_file=True)

    # df['POS_x'].unique()
    df['POS'] = df['POS_x']
    df.drop(['POS_x', 'POS_y', 'url'],axis=1,inplace=True)
    df_db = df[(df['POS'] == 'SS')|(df['POS'] == 'FS')|(df['POS'] == 'CB')]
    df_db['Draft Year'] = year

    # cols = list(df_db.columns)
    # cols_end = [cols[-1], cols[-2]]
    # new_cols = cols[:-2] + cols_end
    new_cols = ['Name', 'Height(in)', 'Weight(lbs)', '40 yard', 'Bench press', 'Vert leap', 'Broad jump',
                'Shuttle', 'HOF', 'College_x', 'College_y', 'Draft Pos', 'Games', 'Draft Year', 'POS']
    df_db = df_db[new_cols]
    print(df_db.info())
    print(df_db.describe())
    print(df_db.head(50))

