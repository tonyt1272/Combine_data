import pandas as pd
import seaborn as sns
from helpers.get_data import get_data

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
    # df = get_data(1995, to_file=False)  # get combine and draft position (if drafted) and games in NFL, just one year
    #
    # a = next_group(df)
    # next(a)  # returns the next 50 player's combine results

    for year in range(1987, 2021):    # get all years at once
        df = get_data(year, to_file=True)
