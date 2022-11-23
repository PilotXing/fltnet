from curses import KEY_ENTER
from urllib import response
import requests
from checkcode import *
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

USERNAME = 'zih.xing'
PASSWORD = 'xing314.'
browser = webdriver.Chrome(executable_path="chromedriver")
browser.set_window_size(1280, 720)

browser.get(Urls.login)
browser.save_screenshot('img/screenshot.png')
cc = Checkcode('img/screenshot.png').to_text()

browser.find_element(By.ID, value='username').send_keys(USERNAME)
browser.find_element(By.ID, value='password').send_keys(PASSWORD)
browser.find_element(By.ID, value='rand').send_keys(cc, KEY_ENTER)
time.sleep(5)  # wait page load
browser.find_element(
    By.XPATH, value='//*[@id="close-popup-image-window"]').click()
flights = browser.find_elements(
    By.XPATH, value='/html/body/div[4]/div[1]/div[2]/div[2]/div[1]/div[2]/div/div[2]/div/table/tbody/tr')
for flight in flights:
    day = flight.find_element(By.XPATH, value='./td[1]/div').text
    date = flight.find_element(By.XPATH, value='./td[2]/div').text
    reg_number = flight.find_element(By.XPATH, value='./td[3]/div').text
    flight_number = flight.find_element(
        By.XPATH, value='./td[4]/div/span/a').text
    flight_route = flight.find_element(
        By.XPATH, value='./td[4]/div').text.partition('\n')[2]
    sign_time = flight.find_element(
        By.XPATH, value='./td[5]/div').text.partition(' - ')[2]
    ETD = flight.find_element(By.XPATH, value='./td[6]/div').text
    roll = flight.find_element(By.XPATH, value='./td[7]/div').text

    print(day, date, reg_number, flight_number,
          sign_time, flight_route, ETD, roll)

    cookies = browser.get_cookies()
    session = requests.session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])



res = session.post(url = Urls.duty, headers=Headers.headers, data=Data.duty)
print(res.json().get('records')[0])


browser.close()
