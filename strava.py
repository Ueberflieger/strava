from argparse import ArgumentParser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import time
import json
import math

def get_activity_type_group(activity):
    group_activity_icon = activity.find_element_by_css_selector('div.group-activity-icon')
    type = group_activity_icon.find_element_by_xpath('.//span[starts-with(@class, "app-icon icon-")]')
    return type.get_attribute('class').split()[1].split("-")[1]


def get_activity_type_single(activity):
    single_activity_icon = activity.find_element_by_css_selector('div.entry-icon.media-left')
    type = single_activity_icon.find_element_by_xpath('.//span[starts-with(@class, "app-icon icon-")]')
    return type.get_attribute('class').split()[1].split("-")[1]

def riding_get_distance(activity):
    stats = activity.find_elements_by_css_selector("div.stat")
    for stat in stats:
        stat_text = stat.find_element_by_css_selector("div.stat-subtext").text
        if stat_text == "Distance":
            dist_str = stat.find_element_by_css_selector("b.stat-text").text
            distance = dist_str.split()[0]
            return float(distance)
    raise Exception("no distance found")

def running_get_distance(activity):
    stats = activity.find_elements_by_css_selector("div.stat")
    for stat in stats:
        stat_text = stat.find_element_by_css_selector("div.stat-subtext").text
        if stat_text == "Distance":
            dist_str = stat.find_element_by_css_selector("b.stat-text").text
            distance = dist_str.split()[0]
            return float(distance)
    raise Exception("no distance found")

def running_get_pace(activity):
    dist_str = ""
    time_str = ""
    stats = activity.find_elements_by_css_selector("div.stat")
    for stat in stats:
        stat_text = stat.find_element_by_css_selector("div.stat-subtext").text
        if stat_text == "Pace":
            pace_str = stat.find_element_by_css_selector("b.stat-text").text.split()[0]
            return paceStr_to_time(pace_str)
        if stat_text == "Distance":
            dist_str = stat.find_element_by_css_selector("b.stat-text").text
        if stat_text == "Time":
            time_str = stat.find_element_by_css_selector("b.stat-text").text
      
    if time_str == "" or dist_str == "":
        raise Exception("no pace")

    return time_distance_to_pace(time_str, dist_str)

def time_distance_to_pace(time_str, dist_str):
    if "h" in time_str:
        time_pattern = '%Hh %Mm'
    else:
        time_pattern = '%Mm %Ss'
    date_time = datetime.strptime(time_str, time_pattern)
    a_timedelta = date_time - datetime(1900, 1, 1)
    sec = a_timedelta.total_seconds()
    distance = dist_str.split()[0]
    pace = sec/float(distance)
    pace_min = pace//60
    pace_sec = math.floor(pace - (pace_min * 60))

    pace_str = f"{pace_min:.0f}:{pace_sec:.0f}"

    return paceStr_to_time(pace_str)

def paceStr_to_time(time_str):
    return datetime.strptime(time_str, '%M:%S').time()

def give_kudos(driver, activity):
    webElement = activity["web_element"]
    try:
        kudos_button = webElement.find_element_by_css_selector("button.btn.btn-icon.btn-icon-only.btn-kudo.btn-xs.js-add-kudo")
    except:
        return
    actions = ActionChains(driver)
    actions.move_to_element(kudos_button).perform()
    time.sleep(2.8)
    kudos_button.click()
    time.sleep(0.2)

def get_athlete_name(activity):
    athlete_name = activity.find_element_by_css_selector("a.entry-owner").text
    return ''.join([i if ord(i) < 128 else '' for i in athlete_name])

def get_athlete_id(activity):
    athlete = activity.find_element_by_css_selector("a.entry-owner")
    return athlete.get_attribute('href').split("/")[-1]

def swimming_get_stats(activity):
    stats = {}

    stats["pace"] = swimming_get_pace(activity)

    return stats

def running_get_stats(activity):
    stats = {}
    
    stats["pace"] = running_get_pace(activity)
    stats["distance"] = running_get_distance(activity)

    return stats

def riding_get_stats(activity):
    stats = {}
    
    stats["distance"] = riding_get_distance(activity)

    return stats

def get_activity_details(type, activityWebElement):
    get_stats_fn = {"run":running_get_stats, "swim": swimming_get_stats, "ride": riding_get_stats}
    activity = {}
    activity["type"] = type
    activity["athlete_name"] = get_athlete_name(activityWebElement)
    activity["athlete_id"] = get_athlete_id(activityWebElement)
    activity["web_element"] = activityWebElement
    if type in get_stats_fn:
        activity["stats"] = get_stats_fn[type](activityWebElement)
    return activity

def scroll_to_end_of_page(driver):
    body = driver.find_element_by_css_selector('body')
    body.send_keys(Keys.END)
    time.sleep(3)

def scroll_to_start_of_page(driver):
    body = driver.find_element_by_css_selector('body')
    body.send_keys(Keys.HOME)
    time.sleep(3)

def fetch_activities(driver, num_activities):

    activities = []
    grouped_activities = []
    single_activities = []
    while len(grouped_activities) + len(single_activities) < num_activities:
        grouped_activities = driver.find_elements_by_css_selector("div.group-activity.feed-entry.card")
        single_activities = driver.find_elements_by_css_selector("div.activity.feed-entry.card")
        scroll_to_end_of_page(driver)
    
    for grouped_activity in grouped_activities:
        type = get_activity_type_group(grouped_activity)
        child_activities = grouped_activity.find_elements_by_css_selector("li.activity.child-entry")
        for child_activity in child_activities:
            activity = get_activity_details(type, child_activity)
            activity["group"] = "yes"
            activities.append(activity)


    for single_activity in single_activities:
        type = get_activity_type_single(single_activity)
        activity = get_activity_details(type, single_activity)
        activity["group"] = "no"
        activities.append(activity)

    scroll_to_start_of_page(driver)
    
    return activities

def running_kudos_check(activity, default_kudos_criteria, athlete_kudos_criteria):
    distance_criteria = None
    pace_criteria = None

    if "distance" in athlete_kudos_criteria:
        distance_criteria = float(athlete_kudos_criteria["distance"])
    elif "distance" in default_kudos_criteria:
        distance_criteria = float(default_kudos_criteria["distance"])

    if "pace" in athlete_kudos_criteria:
        pace_criteria = paceStr_to_time(athlete_kudos_criteria["pace"])
    elif "pace" in default_kudos_criteria:
        pace_criteria = paceStr_to_time(default_kudos_criteria["pace"])

    if distance_criteria == None and pace_criteria == None:
        return 0
    
    distance = activity["stats"]["distance"]
    pace = activity["stats"]["pace"]
    
    print("criteria    =", distance_criteria, pace_criteria)
    print("achievement =", distance, pace)

    if pace_criteria != None and pace <= pace_criteria:
        return 1

    if distance_criteria != None and distance >= distance_criteria:
        return 1

    return 0

def swimming_get_pace(activity):
    stats = activity.find_elements_by_css_selector("div.stat")
    for stat in stats:
        stat_text = stat.find_element_by_css_selector("div.stat-subtext").text
        if stat_text == "Pace":
            pace_str = stat.find_element_by_css_selector("b.stat-text").text.split()[0]
            return paceStr_to_time(pace_str)
      
    raise Exception("no swimming pace")

def swimming_kudos_check(activity, default_kudos_criteria, athlete_kudos_criteria):
    pace_criteria = None

    if "pace" in athlete_kudos_criteria:
        pace_criteria = paceStr_to_time(athlete_kudos_criteria["pace"])
    elif "pace" in default_kudos_criteria:
        pace_criteria = paceStr_to_time(default_kudos_criteria["pace"])

    if pace_criteria == None:
        return 0

    pace = activity["stats"]["pace"]
    
    print("criteria    =", pace_criteria)
    print("achievement =", pace)

    if pace_criteria != None and pace <= pace_criteria:
        return 1

    return 0

def riding_kudos_check(activity, default_kudos_criteria, athlete_kudos_criteria):
    distance_criteria = None

    if "distance" in athlete_kudos_criteria:
        distance_criteria = float(athlete_kudos_criteria["distance"])
    elif "distance" in default_kudos_criteria:
        distance_criteria = float(default_kudos_criteria["distance"])

    if distance_criteria == None:
        return 0

    distance = activity["stats"]["distance"]
    
    print("criteria    =", distance_criteria)
    print("achievement =", distance)

    if distance >= distance_criteria:
        return 1

    return 0

def kudos_check_activity_not_supported(activity, default_kudos_criteria, athlete_kudos_criteria):
    print("activity not supported")
    return 0

def get_kudos_check_fn(type):
    supported_activities = {"run": running_kudos_check, "swim": swimming_kudos_check, "ride": riding_kudos_check}

    if type not in supported_activities:
        return kudos_check_activity_not_supported

    return supported_activities[type]

def get_default_kudos_criteria(type, config):
    if type in config["default"]:
        return config["default"][type]
    return {}

def get_athlete_kudos_criteria(type, athlete_id, config):
    if athlete_id in config["athletes"] and type in config["athletes"][athlete_id]["criteria"]:
        return config["athletes"][athlete_id]["criteria"][type]
    return {}

def is_athlete_vip(athlete_id, config):
    return athlete_id in config["vip"]
        
def is_athlete_on_ignore_list(athlete_id, config):
    return athlete_id in config["ignore"]

def strava_login(user, pw):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = True
    chrome_options.add_argument("--disable-plugins-discovery");
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    url = "https://www.strava.com/login"
    print(url)
    
    driver = webdriver.Chrome("/usr/bin/chromedriver", options=chrome_options)
                
    driver.delete_all_cookies()
    driver.get(url)
    
    email = driver.find_element_by_id("email")
    password = driver.find_element_by_id("password")
    login = driver.find_element_by_id("login-button")
    
    email.send_keys(user);
    password.send_keys(pw);
    login.click()
    return driver

def group_kudos_for_all(config):
    return config["group_activity_all_kudos"] == "yes"

def check_activities(driver, config):
    
    activities = fetch_activities(driver, 10)
    
    for activity in activities:
        type = activity["type"]
        athlete_id = activity["athlete_id"]
        athlete_name = activity["athlete_name"]

        print(type, athlete_id, athlete_name)
        
        if is_athlete_on_ignore_list(athlete_id, config):
            print("is ignore")
            kudos = 0
        elif is_athlete_vip(athlete_id, config):
            print("is vip")
            kudos = 1
        elif activity["group"] == "yes" and group_kudos_for_all(config):
            print("is group")
            kudos = 1
        else:
            kudos_check_fn = get_kudos_check_fn(type)
            default_kudos_criteria = get_default_kudos_criteria(type, config)
            athlete_kudos_criteria = get_athlete_kudos_criteria(type, athlete_id, config)
            kudos = kudos_check_fn(activity, default_kudos_criteria, athlete_kudos_criteria)

        if kudos:
            print(f"  KUDOS {athlete_name}")
            give_kudos(driver, activity)
        else:
            print(f"  Sorry {athlete_name}, no kudos")
        print()

    driver.quit()


parser = ArgumentParser()
parser.add_argument("-p", "--password", dest="password", help="Password for strava, won't be stored", required=True)
parser.add_argument("-u", "--username", dest="username", help="Username for strava", required=True)

args = parser.parse_args()

if __name__ == "__main__":
    with open('config.json') as json_file:
        config = json.load(json_file)

    driver = strava_login(args.username, args.password)
    check_activities(driver, config)
