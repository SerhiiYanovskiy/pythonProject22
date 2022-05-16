from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import re

def get_fedex(trak):
    opts = Options()
    opts.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    driver.set_window_position(0, 0)
    driver.set_window_size(1920, 1080)
    driver.get("https://www.fedex.com/fedextrack/")
    time.sleep(2)
    click = "/html/body/div[1]/div/div/div[2]/ul[2]/li[2]/button"
    driver.find_element_by_xpath(click).click()
    input_track = "/html/body/div[1]/div/div/div[2]/div[2]/div/form/input"
    driver.find_element_by_xpath(input_track).send_keys("776783001175")
    driver.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/div[2]/div/form/button").click()
    time.sleep(3)
    main_page = driver.page_source
    soup = BeautifulSoup(main_page, "html")
    status = soup.find("div", class_="detail-page-default").find("h1")
    return status.text


def get_usp(track):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.set_window_position(0, 0)
    driver.set_window_size(1920, 1080)
    driver.get(f"https://www.ups.com/track?loc=en_US&requester=QUIC&tracknum={track}/trackdetails")
    time.sleep(1)
    main_page = driver.page_source
    soup = BeautifulSoup(main_page, "html")
    status = soup.find("div", class_="ng-star-inserted").find_all("span")
    return str(status[1].text.split(" ")[1])

def get_usps(track):
    opts = Options()
    opts.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    driver.set_window_position(0, 0)
    driver.set_window_size(1920, 1080)
    driver.get(f"https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1={track}")
    time.sleep(3)
    main_page = driver.page_source
    soup = BeautifulSoup(main_page, "html")
    status = soup.find("div", class_="delivery_status").find("strong").text
    return status.split(" ")[0]