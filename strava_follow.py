from argparse import ArgumentParser
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from strava_login import strava_login
import time

def follow_people(driver):
    url = "https://www.strava.com/dashboard"
    driver.get(url)

    card = driver.find_element_by_css_selector('div.card-body.text-center')
    link = card.find_element_by_xpath('.//a[starts-with(@href, "/athletes/")]')
    id = link.get_attribute('href').split('/')[-1]
  
    page = 1
    new_followees = 0
    while True:
        url = f'https://www.strava.com/athletes/{id}/follows?page={page}&type=followers' 
        page = page + 1
        driver.get(url)
        print(url)
        time.sleep(3)
       
        # check if there is a list with followers
        athlete_list = driver.find_element_by_css_selector('ul.following.list-athletes.with-menu.show-actions')
        elements = athlete_list.find_elements_by_css_selector("div.avatar.avatar-athlete.avatar-default")

        if len(elements) == 0:
            # at the end of the follower list
            break
        
        try:
            follow_buttons = driver.find_elements_by_css_selector('button.primary.button.btn-primary.follow.fixed-small')
        except:
            # continue with the next page
            continue
        
        for follow_button in follow_buttons:
            actions = ActionChains(driver)
            actions.move_to_element(follow_button).perform()
            time.sleep(0.5)
            follow_button.click()
            new_followees = new_followees + 1
    
    return new_followees

parser = ArgumentParser()
parser.add_argument("-p", "--password", dest="password", help="Password for strava, won't be stored", required=True)
parser.add_argument("-u", "--username", dest="username", help="Username for strava", required=True)

args = parser.parse_args()

if __name__ == "__main__":

    driver = strava_login(args.username, args.password)
    new_people  = follow_people(driver)

    print(f"following {new_people} new people")

    driver.quit()

