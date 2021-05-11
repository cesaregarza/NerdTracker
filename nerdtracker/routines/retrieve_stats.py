import urllib.parse
from bs4 import BeautifulSoup
from ..constants.tracker_columns import tracker_columns

def retrieve_stats_from_tracker(scraper, activision_user_string):
    activision_user_string = str(activision_user_string)
    tracker_url = f"https://cod.tracker.gg/modern-warfare/profile/atvi/{urllib.parse.quote(activision_user_string)}/mp"
    request = scraper.get(tracker_url)

    soup = BeautifulSoup(request.content, 'html.parser')

    all_stats = soup.find_all('div', {'class': 'numbers'})

    stat_dict = {key: None for key in tracker_columns.stat_columns}

    for stat_soup in all_stats[:-4]:
        name        = stat_soup.find(class_="name").string
        value       = stat_soup.find(class_="value").string
        try:
            rank    = stat_soup.find(class_="rank").string
        except AttributeError:
            rank    = ""

        stat_dict[name] = value
    
    return stat_dict