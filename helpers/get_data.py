import pandas as pd
from helpers.get_combine import get_combine
from helpers.get_player_draft import get_player_draft
from helpers.switch_name_lnf import switch_name_lnf
from helpers.my_paths import data_path, data_path_merged


def get_data(year_int=1987, to_file=True):
    data_year = str(year_int)

    # get_combine(data_year, to_file=True)

    try:
        df_combine = pd.read_csv(data_path(f'combine\\nfl_combine_{data_year}'))
    except FileNotFoundError:
        try:
            df_combine = pd.read_csv(f'nfl_combine_{data_year}')
        except FileNotFoundError:
            df_combine = get_combine(data_year, to_file=True)

    df_combine['Name'] = df_combine.apply(switch_name_lnf, axis=1)
    df_combine.drop('player_id', axis=1, inplace=True)
    df_combine.drop('Year', axis=1, inplace=True)

    players, columns = get_player_draft(year=year_int)
    df = pd.DataFrame(data=players, columns=columns)
    df['Name'] = df.apply(switch_name_lnf, axis=1)

    df2 = pd.merge(df_combine, df, how='left', on='Name',
                   left_index=False, right_index=False, sort=False,
                   suffixes=('_x', '_y'), copy=True, indicator=False,
                   validate=None)

    df3 = df2.sort_values('Draft Pos').reset_index()
    df3.drop(['index', 'Wonderlic', 'Draft Year', '3Cone'], axis=1, inplace=True)

    draft_position = df3['Draft Pos']
    for i, item in enumerate(draft_position):
        if i > 0:
            try:
                if draft_position[i] == draft_position[i-1]:
                    if df3.loc[i]['College_x'][0] != df3.loc[i]['College_y'][0]:
                        df3.drop(i, inplace=True)
                    elif df3.loc[i-1]['College_x'][0] != df3.loc[i-1]['College_y'][0]:
                        df3.drop(i-1, inplace=True)
            except :
                pass

    df3.reset_index(inplace=True, drop=True)
    print(data_year)
    print(df3.loc[0:50])

    if to_file:
        file_name = f'nfl_combine_{data_year}_merged_draft'
        try:
            file_path = data_path_merged(file_name)
            df3.to_csv(file_path, index=False)
        except FileNotFoundError:
            file_path = f'{file_name}'
            df3.to_csv(file_path, index=False)

    return df3
