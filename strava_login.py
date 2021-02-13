from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def strava_login(user, pw):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = True
    chrome_options.add_argument("--disable-plugins-discovery");
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    url = "https://www.strava.com/login"
    print(url)
    
    driver = webdriver.Chrome("/usr/bin/chromedriver", options=chrome_options)
    driver.set_window_size(1920, 1080)

    driver.delete_all_cookies()
    driver.get(url)
    
    email = driver.find_element_by_id("email")
    password = driver.find_element_by_id("password")
    login = driver.find_element_by_id("login-button")
    
    email.send_keys(user);
    password.send_keys(pw);
    login.click()
    return driver

