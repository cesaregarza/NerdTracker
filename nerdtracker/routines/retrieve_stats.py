import urllib.parse
from bs4 import BeautifulSoup
from ..constants.tracker_columns import tracker_columns
from cloudscraper import CloudScraper

def retrieve_stats_from_tracker(scraper:CloudScraper, activision_user_string:str):
    """Retrieve stats from tracker.gg, returning a StatsObject

    Args:
        scraper (CloudScraper): CloudScraper object
        activision_user_string (str): Activision user string

    Returns:
        StatsObject: StatsObject object
    """
    from ..classes.stats_object import StatsObject
    # Retrieve stats from tracker.gg using the activision user ID
    activision_user_string = str(activision_user_string)
    tracker_url = f"https://cod.tracker.gg/modern-warfare/profile/atvi/{urllib.parse.quote(activision_user_string)}/mp"
    request = scraper.get(tracker_url)

    # Parse the tracker.gg page using BeautifulSoup
    soup = BeautifulSoup(request.content, 'html.parser')

    all_stats = soup.find_all('div', {'class': 'numbers'})

    #Generate a dictionary of stats, which will remain None if the page is not found
    stat_dict = {key: None for key in tracker_columns.stat_columns}

    # If the page is found, fill the dictionary with the stats
    for stat_soup in all_stats[:-4]:
        name        = stat_soup.find(class_="name").string
        value       = stat_soup.find(class_="value").string
        stat_dict[name] = value
    
    # Return a StatsObject object
    return StatsObject(stat_dict, tracker=True)