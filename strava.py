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

def stats_distance_km_get(activity):
    stats = activity.find_elements_by_css_selector("div.stat")
    for stat in stats:
        stat_text = stat.find_element_by_css_selector("div.stat-subtext").text
        if stat_text == "Distance":
            dist_str = stat.find_element_by_css_selector("b.stat-text").text
            distance = dist_str.split()[0]
            return float(distance)
    raise Exception("no distance found")

def timeStr_to_time(time_str):
    if "h" in time_str:
        time_pattern = '%Hh %Mm'
    elif "s" in time_str:
        time_pattern = '%Mm %Ss'
    elif ":" in time_str:
        time_pattern = '%H:%M:%S'
    else:
        Exception("Invalid time string", time_str)

    date_time = datetime.strptime(time_str, time_pattern)
    return date_time - datetime(1900, 1, 1)

def stats_time_get(activity):
    stats = activity.find_elements_by_css_selector("div.stat")
    for stat in stats:
        stat_text = stat.find_element_by_css_selector("div.stat-subtext").text
        if stat_text == "Time":
            time_str = stat.find_element_by_css_selector("b.stat-text").text
            return timeStr_to_time(time_str)
    raise Exception("no time found")

def stats_pace_km_get(activity):
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
        activity["kudos"] = "already given"
        return 0
    actions = ActionChains(driver)
    actions.move_to_element(kudos_button).perform()
    time.sleep(2)
    kudos_button.click()
    activity["kudos"] = "given"
    return 1

def to_ascii(str):
    return ''.join([i if ord(i) < 128 else '' for i in str])

def get_athlete_name(activity):
    athlete_name = activity.find_element_by_css_selector("a.entry-owner").text
    return to_ascii(athlete_name)

def get_athlete_id(activity):
    athlete = activity.find_element_by_css_selector("a.entry-owner")
    return athlete.get_attribute('href').split("/")[-1]

def stats_distance_m_get(activity):
    stats = activity.find_elements_by_css_selector("div.stat")
    for stat in stats:
        stat_text = stat.find_element_by_css_selector("div.stat-subtext").text
        if stat_text == "Distance":
            dist_str = stat.find_element_by_css_selector("b.stat-text").text
            distance = dist_str.split()[0].replace(",","")
            return float(distance)
    raise Exception("no distance found")

def get_activity_details(type, activityWebElement, config):
    stats_functions = {
            "distance_km": stats_distance_km_get,
            "distance_m": stats_distance_m_get,
            "pace_km": stats_pace_km_get,
            "pace_100m": stats_pace_100m_get,
            "time": stats_time_get,
            }

    activity = {}
    activity["athlete_name"] = get_athlete_name(activityWebElement)
    activity["athlete_id"] = get_athlete_id(activityWebElement)
    activity["web_element"] = activityWebElement
    activity["type"] = type

    if type not in config["stats"]:
        print(type, "not supported")
        return activity
    
    stats = {}
    for key in config["stats"][type]:
        stats[key] = stats_functions[key](activityWebElement)
    activity["stats"] = stats
    print(type, stats)

    return activity

def scroll_to_end_of_page(driver):
    body = driver.find_element_by_css_selector('body')
    body.send_keys(Keys.END)
    #time.sleep(3)

def scroll_to_start_of_page(driver):
    body = driver.find_element_by_css_selector('body')
    body.send_keys(Keys.HOME)
    #time.sleep(3)

def get_activity_type(driver, activity):
    activity_url = activity.find_element_by_xpath('.//a[starts-with(@href, "/activities/")]')
    activity_id = activity_url.get_attribute('href').split('/')[-1]

    origin_window = driver.current_window_handle

    url = f"https://www.strava.com/activities/{activity_id}"

    driver.execute_script(f"window.open('{url}', 'activity')")

    driver.switch_to_window(driver.window_handles[-1])
    type = driver.find_element_by_css_selector("span.title").text
    driver.close()
    
    driver.switch_to_window(origin_window)

    type = to_ascii(type.split('–')[1].replace(" ", "").lower())

    return type

def fetch_activities(driver, num_activities, config):

    activities = []
    grouped_activities = []
    single_activities = []
    while len(grouped_activities) + len(single_activities) < num_activities:
        grouped_activities = driver.find_elements_by_css_selector("div.group-activity.feed-entry.card")
        single_activities = driver.find_elements_by_css_selector("div.activity.feed-entry.card")
        scroll_to_end_of_page(driver)
    
    for grouped_activity in grouped_activities:
        child_activities = grouped_activity.find_elements_by_css_selector("li.activity.child-entry")
        for child_activity in child_activities:
            type = get_activity_type(driver, child_activity)
            activity = get_activity_details(type, child_activity, config)
            activity["group"] = "yes"
            activities.append(activity)

    for single_activity in single_activities:
        type = get_activity_type(driver, single_activity)
        activity = get_activity_details(type, single_activity, config)
        activity["group"] = "no"
        activities.append(activity)

    scroll_to_start_of_page(driver)
    
    return activities

def convert_to_compareable(value, criteria):

    if criteria == "distance_km" or criteria == "distance_m":
        return float(value)

    if criteria == "pace_km" or criteria == "pace_100m":
        return paceStr_to_time(value)

    if criteria == "time":
        return timeStr_to_time(value)

    print("invalid criteria", criteria, value)
    return None

def kudos_check(activity, user_cfg, config):

    type = activity["type"]
    athlete_id = activity["athlete_id"]

    if type not in config["stats"]:
        print(type, "not supported")
        return 0
    
    criterias = config["stats"][type]

    targets = {}
    for criteria in criterias:
        try:
            targets[criteria] = user_cfg["athletes"][athlete_id]["criteria"][type][criteria]
        except:
            pass

        if criteria not in targets:
            try:
                targets[criteria] = user_cfg["default"][type][criteria]
            except:
                pass
            
    for criteria in targets:
        target = targets[criteria]
        target = convert_to_compareable(target, criteria)

        achieved = activity["stats"][criteria]
        
        print(criteria, achieved, target)
        if config["whats_better"][criteria] == "more":
            if achieved >= target:
                return 1
        else:
            if achieved <= target:
                return 1

    return 0

def stats_pace_100m_get(activity):
    stats = activity.find_elements_by_css_selector("div.stat")
    for stat in stats:
        stat_text = stat.find_element_by_css_selector("div.stat-subtext").text
        if stat_text == "Pace":
            pace_str = stat.find_element_by_css_selector("b.stat-text").text.split()[0]
            return paceStr_to_time(pace_str)
      
    raise Exception("no swimming pace")

def is_athlete_vip(athlete_id, user_cfg):
    return athlete_id in user_cfg["vip"]
        
def is_athlete_on_ignore_list(athlete_id, user_cfg):
    return athlete_id in user_cfg["ignore"]

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

def group_kudos_for_all(user_cfg):
    return user_cfg["group_activity_all_kudos"] == "yes"

def check_activities(driver, user_cfg, config):
    total_kudos = 0    
    activities = fetch_activities(driver, 50, config)
    
    for activity in activities:
        type = activity["type"]
        athlete_id = activity["athlete_id"]
        athlete_name = activity["athlete_name"]

        print(type, athlete_id, athlete_name)
        
        if is_athlete_on_ignore_list(athlete_id, user_cfg):
            print("is ignore")
            kudos = 0
        elif is_athlete_vip(athlete_id, user_cfg):
            print("is vip")
            kudos = 1
        elif activity["group"] == "yes" and group_kudos_for_all(user_cfg):
            print("is group")
            kudos = 1
        else:
            kudos = kudos_check(activity, user_cfg, config)

        if kudos:
            total_kudos = total_kudos + give_kudos(driver, activity)
            print(f"  KUDOS to {athlete_name} {activity['kudos']}")
        else:
            print(f"  Sorry {athlete_name}, no kudos")
        print()
    return total_kudos

parser = ArgumentParser()
parser.add_argument("-p", "--password", dest="password", help="Password for strava, won't be stored", required=True)
parser.add_argument("-u", "--username", dest="username", help="Username for strava", required=True)

args = parser.parse_args()

if __name__ == "__main__":
    with open('user.json') as json_file:
        user_cfg = json.load(json_file)
    
    with open('config.json') as json_file:
        config = json.load(json_file)

    driver = strava_login(args.username, args.password)
    kudos_given = check_activities(driver, user_cfg, config)

    print(kudos_given, "Kudos given")

    driver.quit()
