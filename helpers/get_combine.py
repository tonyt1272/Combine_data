import re
import pandas as pd
from selenium import webdriver
from time import sleep
from numpy.random import randn
from bs4 import BeautifulSoup as bs
from helpers.my_paths import data_path, data_path_combine


def get_combine(year=1987, to_file=False):
    """
    Polite, slow scraping with Selenium
    :param year: NFL draft year
    :param to_file: Boolean, True: saves dataframe to file, False: just returns df to console
    :return: columns: ['Year', 'Name', 'College', 'POS', 'Height(in)', 'Weight(lbs)', 'Wonderlic', '40 yard',
                     'Bench press', 'Vert leap', 'Broad jump', 'Shuttle', '3Cone']
    """
    # scraping with Selenium
    year_str = str(year)

    try:
        driver = webdriver.Chrome(data_path('chromedriver.exe'))
    except:
        driver = webdriver.Chrome('chromedriver.exe')
    driver.implicitly_wait(5)  # when selecting elements wait 5 seconds for the element to load before exception
    mu = 7
    var = 2
    human_scan_time = mu + var * randn()  # Scan like a person
    if human_scan_time < 0:
        human_scan_time = 1
    try:

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
                # print(item)
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
