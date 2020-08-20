import os
import re
import pandas as pd
import seaborn as sns
import requests_html as r_html
from selenium import webdriver
from time import sleep
from numpy.random import randn
from bs4 import BeautifulSoup as bs


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


def data_path(file_name):
    return os.path.join('C:\\Users', 'Anthony', 'Desktop', 'data', file_name)


def data_path_combine(file_name):
    return os.path.join('C:\\Users', 'Anthony', 'Desktop', 'data', 'Combine', file_name)


def data_path_merged(file_name):
    return os.path.join('C:\\Users', 'Anthony', 'Desktop', 'data', 'Combine_Merged_Draft', file_name)


def get_combine(year=1987, to_file=False):
    """
    Polite, slow scraping with Selenium
    :param year: NFL draft year
    :param to_file: Boolean, True: saves dataframe to file, False: just returns df to console
    :return: columns: ['Year', 'Name', 'College', 'POS', 'Height(in)', 'Weight(lbs)', 'Wonderlic', '40 yard',
                     'Bench press', 'Vert leap', 'Broad jump', 'Shuttle', '3Cone']
    """
    # scraping with Selenium
    driver = webdriver.Chrome(data_path('chromedriver.exe'))
    driver.implicitly_wait(5)  # when selecting elements wait 5 seconds for the element to load before exception
    mu = 7
    var = 2
    human_scan_time = mu + var * randn()  # Scan like a person
    if human_scan_time < 0:
        human_scan_time = 1
    try:
        year_str = str(year)
        url = f'https://nflcombineresults.com/nflcombinedata.php?year={year_str}&pos=&college='
        driver.get(url)
        sleep(human_scan_time)
        response_text = driver.page_source
        text_soup = bs(response_text, 'lxml')
        table_data_soup = text_soup.find_all('table')[0]
        table_data = table_data_soup.find_all('td')
        table_data2 = [list(item.children)[0] for item in table_data]  # elements of table_data2 are bs4.element.Tag
        table_data2_str_lst = [str(item) for item in table_data2]      # objects
        pattern = re.compile(r'<a href="https://nflcombineresults\.com/playerpage\.php\?.*">')

        for i, item in enumerate(table_data2_str_lst):
            if '<div align="center">' in item:
                item = item.replace('<div align="center">', '')
                item = item.replace('</div>', '')
                table_data2_str_lst[i] = item

            if '<div align="center" style="visibility:hidden;">' in item:
                item = item.replace('<div align="center" style="visibility:hidden;">', '')
                item = item.replace('</div>', '')
                item = item.replace('9.99', '')
                table_data2_str_lst[i] = item

            if '<a href' in item:
                print(item)
                valid = pattern.findall(item)
                table_data2_str_lst[i] = item.replace(valid[0], '').strip()
                table_data2_str_lst[i] = table_data2_str_lst[i].replace('</a>', '').strip()
            # print(item)

        columns_a = ['Year', 'Name', 'College', 'POS', 'Height(in)', 'Weight(lbs)', 'Wonderlic', '40 yard',
                     'Bench press', 'Vert leap', 'Broad jump', 'Shuttle', '3Cone']
        data = table_data2_str_lst[13:-1]

        data_table = []
        for i in range(0, len(data), 13):
            data_table.append(data[i:i+13])

        data_df = pd.DataFrame(data_table, columns=columns_a)
        data_df['player_id'] = data_df['Year'] + data_df.index.astype(str)

        if to_file:
            file_name = f'nfl_combine_{year}'
            try:
                file_path = data_path_combine(file_name)
                data_df.to_csv(file_path, index=False)
            except FileNotFoundError:
                file_path = f'{file_name}'
                data_df.to_csv(file_path, index=False)

    except IndexError:
        print(f'Load failed{year_str}')

    driver.close()
    driver.quit()
    return data_df


def get_player_draft(year=1987):
    """
    Scraping with requests_html

    :param year: NFL draft year
    :return: 2d list for all players in that draft year, can be easily converted to
    dataFrame
    ['url', 'Name', 'HOF', 'POS', 'College', 'Draft Pos', 'Games', 'Draft Year']
    """

    player_urls = []
    domain = 'https://www.pro-football-reference.com'
    url = f'https://www.pro-football-reference.com/years/{year}/draft.htm'
    session = r_html.HTMLSession()
    r = session.get(url)
    draft_table_element_rows = r.html.xpath('//table/tbody//tr')
    num_rows = len(draft_table_element_rows)

    for row in range(0, num_rows):
        element_row = draft_table_element_rows[row]
        try:
            player_name = element_row.xpath('//td')[2].text

            player_name_list = player_name.split(' ')
            if player_name_list[-1] == 'HOF':
                player_hof = 1
            else:
                player_hof = 0

        except:
            continue

        try:
            player_pos = element_row.xpath('//td')[3].text
        except:
            player_pos = 'error'

        player_draft_pos = int(element_row.xpath('//td')[0].text)

        if len(element_row.xpath('//td/a')) > 2:
            player_url = element_row.xpath('//td/a')[1].attrs['href']
            player_url_final = domain + player_url
        else:
            player_url_final = 'place_holder'

        try:
            player_games_played = int(element_row.xpath('//td')[11].text)
        except:
            player_games_played = 0
        try:
            if year < 1994:  # Sacks column added to player stats in 1994
                player_college = element_row.xpath('//td')[25].text
            else:
                player_college = element_row.xpath('//td')[26].text
        except:
            player_college = ""

        player_urls.append((player_url_final, player_name, player_hof, player_pos, player_college,
                            player_draft_pos, player_games_played, year))
    columns_a = ['url', 'Name', 'HOF', 'POS', 'College', 'Draft Pos', 'Games', 'Draft Year']
    return player_urls, columns_a
    # players_df = pd.DataFrame(data=player_urls, columns=columns_a)
    # return players_df


def switch_name_lnf(name):
    """
    No unique, consistent identifier exists between the Combine and draft data sets.  I create one here using last name
    and first two initials of the first name.  If there are two or more players with the same last,fi[0:2] then the
    first letter of the school is used to differentiate.  Again, this is because of the lack of consistency in naming
    between datasets.  Trying to use the entire name does not work.  For example, data set one uses Michael, data set
    two uses Mike, etc.
    :param name: first last
    :return: last,fi
    """
    old_name = name['Name']
    # print(old_name)
    # college = name['College'][0]
    old_name_list = old_name.split(' ')
    try:
        if "'" in old_name_list[0]:
            old_name_list[0] = old_name_list[0].replace("'", "")
    except IndexError:
        pass

    try:
        if "'" in old_name_list[-1]:
            old_name_list[-1] = old_name_list[-1].replace("'", "")
    except IndexError:
        pass

    if len(old_name_list[0]) == 1 and len(old_name_list[1]) == 1 and len(old_name_list) > 2:
        first = old_name_list[0] + old_name_list[1]
        last = old_name_list[-1]
        old_name_list = [first, last]
    try:
        if '.' in old_name_list[0]:
            old_name_list[0] = old_name_list[0].replace('.', '')
    except IndexError:
        pass

    # This if block is necessary because of inconsistencies in player naming between data sets
    if old_name_list[-1] == 'HOF' or old_name_list[-1] == 'III' or old_name_list[-1] == 'Jr.' or \
            old_name_list[-1] == 'II' or old_name_list[-1] == 'Sr.':
        old_name_list.pop()
    try:
        new_name = old_name_list[-1] + ',' + old_name_list[0][0:2]
    except IndexError:
        new_name = old_name_list[-1] + ',' + old_name_list[0][0]

    new_name = new_name.lower()
    return new_name.strip()


def get_data(year_int=1987, to_file=True):
    data_year = str(year_int)

    try:
        df_combine = pd.read_csv(data_path(f'combine\\nfl_combine_{data_year}'))
    except FileNotFoundError:
        df_combine = pd.read_csv(f'nfl_combine_{data_year}')

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
            except IndexError:
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


def next_group():
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

    df = get_combine(1988, to_file=True)   # run this before get_data().
    #
    # for year in range(1987, 2021):    # get it all at once
    #     get_combine(year, to_file=False)
    #     print(f'{year} saved successfully')

    df = get_data(1988, to_file=True)  # requires combine files to be present in cwd or directory -> data_path_combine()
    # for year in range(1987, 2021):
    #     get_data(year, to_file=True)
    a = next_group()
    # next(a)  # returns the next 50 player's combine results



