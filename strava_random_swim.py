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

def get_random_distance_m(min, max, mod=0):
    if min < 0 or max < 0:
        Exception("invalid range")
    if mod == 0:
        return random.randint(min, max)
    return int(random.randint(min, max)/mod) * mod;

def get_motivation_str():
    motivation = ["Yay!", "DONE!", "feeling great", "tough but worth it", "Did it!", "Did it",
            "", "So spent", "Morning Swim"]
    return random.choice(motivation)

def get_title(distance):

    laps = str(int(distance/50))

    first_part = random.choice([f"{laps} Laps!",""])

    second_part = get_motivation_str()
    if first_part == "":
        while second_part == "":
            second_part = get_motivation_str()

    title = f"{first_part} {second_part}".strip()

    return title


def manual_activity_set_type(driver, type):
    activity_upload_type = driver.find_element_by_css_selector('div.upload-type')
    activity_type_dropdown = activity_upload_type.find_element_by_css_selector("div.selection")

    activity_type_dropdown.click()

    options = activity_upload_type.find_elements_by_css_selector('li')

    for option in options:
        if option.text == "Swim":
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

def manual_activity_set_distance_m(driver, distance_m):
    unit_element = driver.find_element_by_css_selector('div.input-field.input-field-joined.upload-unit')
    unit_dropdown = unit_element.find_element_by_css_selector("div.selection")
    unit_dropdown.click()

    options = unit_element.find_elements_by_css_selector('li')

    for option in options:
        if option.text == "meters":
            option.click()
            break;

    meter_input = driver.find_element_by_id("activity_distance")
    meter_input.clear()
    meter_input.send_keys(str(distance_m))

def manual_activity_set_title(driver, title):
    title_input = driver.find_element_by_id("activity_name")
    title_input.clear()
    title_input.send_keys(title)

def manual_activity_create_click(driver):
    upload_controls = driver.find_element_by_css_selector("div.row.upload-controls.mb-xl")
    create_button = upload_controls.find_element_by_css_selector("input.btn-primary")
    create_button.click()

def manual_swim_activity(driver):
    url = "https://www.strava.com/upload/manual"
    driver.get(url)

    hours = 0
    min = get_random_minutes(38,50)
    sec = get_random_seconds()

    manual_activity_set_type(driver, "Swim")
    manual_activity_set_time(driver, hours, min, sec)

    distance = get_random_distance_m(1500, 2500, 100) # 50m pool length
    manual_activity_set_distance_m(driver, distance)

    title = get_title(distance)
    manual_activity_set_title(driver, title)

    manual_activity_create_click(driver)
    
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--password", dest="password", help="Password for strava, won't be stored", required=True)
    parser.add_argument("-u", "--username", dest="username", help="Username for strava", required=True)

    args = parser.parse_args()

    driver = strava_login(args.username, args.password)

    manual_swim_activity(driver)

    driver.quit()

