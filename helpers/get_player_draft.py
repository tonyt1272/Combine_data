import requests_html as r_html


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