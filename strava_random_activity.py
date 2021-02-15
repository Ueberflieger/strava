from argparse import ArgumentParser
from selenium import webdriver
from strava_login import strava_login
from strava_random_yoga import manual_yoga_activity 
from strava_random_swim import manual_swim_activity 
from strava_random_workout import manual_workout_activity 
import random

def do_random_activity(driver):
    activities = [manual_yoga_activity, manual_workout_activity, manual_swim_activity]
    
    choice = random.choice(activities)
    choice(driver)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--password", dest="password", help="Password for strava, won't be stored", required=True)
    parser.add_argument("-u", "--username", dest="username", help="Username for strava", required=True)
    parser.add_argument("-r", "--probability", dest="probability", help="Probability of an activity happening", default = 1, required=True)
    
    args = parser.parse_args()

    probability = float(args.probability)
    if probability > 1:
        probability = 1
    
    random.seed()
    r = random.random() 
    if r < probability:
        driver = strava_login(args.username, args.password)
        do_random_activity(driver)
        driver.quit()


    


