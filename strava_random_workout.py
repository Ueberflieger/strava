from argparse import ArgumentParser
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from strava_login import strava_login
import time
import random

def get_random_minutes(min = 0, max = 59):
    if min < 0 or max > 59:
        Exception("invalid range")
    return random.randint(min, max)

def get_random_seconds(min = 0, max = 59):
    if min < 0 or max > 59:
        Exception("invalid range")
    return random.randint(min, max)

def get_random_title():
    titles = ["Legs", "Upper Body", "Easy Session", "Skipping", "Group workout", "Focus on back", "Focus on my back"]
    return random.choice(titles)

def manual_activity_set_type(driver, type):
    activity_upload_type = driver.find_element_by_css_selector('div.upload-type')
    activity_type_dropdown = activity_upload_type.find_element_by_css_selector("div.selection")

    activity_type_dropdown.click()

    options = activity_upload_type.find_elements_by_css_selector('li')

    for option in options:
        if option.text == type:
            option.click()
            break;

def manual_activity_set_time(driver, hours, min, sec):

    hours_input = driver.find_element_by_id("activity_elapsed_time_hours")
    hours_input.clear()
    hours_input.send_keys(str(hours))
    
    min_input = driver.find_element_by_id("activity_elapsed_time_minutes")
    min_input.clear()
    min_input.send_keys(str(min))
    
    sec_input = driver.find_element_by_id("activity_elapsed_time_seconds")
    sec_input.clear()
    sec_input.send_keys(str(sec))

def manual_activity_set_title(driver, title):
    title_input = driver.find_element_by_id("activity_name")
    title_input.clear()
    title_input.send_keys(title)

def manual_activity_create_click(driver):
    upload_controls = driver.find_element_by_css_selector("div.row.upload-controls.mb-xl")
    create_button = upload_controls.find_element_by_css_selector("input.btn-primary")
    #create_button.click()

def manual_workout_activity(driver):
    url = "https://www.strava.com/upload/manual"
    driver.get(url)

    hours = 0
    min = get_random_minutes(30,59)
    sec = get_random_seconds()

    manual_activity_set_type(driver, "Workout")
    manual_activity_set_time(driver, hours, min, sec)

    title = get_random_title()
    manual_activity_set_title(driver, title)

    manual_activity_create_click(driver)
    
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--password", dest="password", help="Password for strava, won't be stored", required=True)
    parser.add_argument("-u", "--username", dest="username", help="Username for strava", required=True)

    args = parser.parse_args()

    driver = strava_login(args.username, args.password)

    manual_workout_activity(driver)

    driver.quit()

