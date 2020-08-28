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