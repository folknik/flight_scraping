import os
import json
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


url = os.environ['url']
minutes = int(os.environ['minutes'])


def set_chrome_options():
    options = Options()
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugin-port=9222")
    options.add_argument("--screen-size=1200x800")
    return options


def insert_data(data):
    print(f"{len(data)} flights were found")


def process_data(data):
    arr = []
    for key in data.keys():
        if isinstance(data[key], list):
            content = data[key]
            hexident = content[0]
            from_airport = content[11]
            to_airport = content[12]
            if hexident and from_airport and to_airport:
                print("hexident: {}, from {}, to {}".format(hexident, from_airport, to_airport))
                arr.append((hexident, from_airport, to_airport))
    insert_data(arr)


def main(web_url):
    print(f"\n\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, scraping has started")
    driver = webdriver.Chrome(options=set_chrome_options())
    driver.get(web_url)
    contents = json.loads(driver.find_element_by_tag_name('pre').text)
    driver.close()
    process_data(contents)


if __name__ == '__main__':
    # url = "https://data-live.flightradar24.com/zones/fcgi/feed.js?bounds=56.50,55.00,36.28,38.86&faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=1&estimated=1&maxage=14400&gliders=1&stats=1"
    while True:
        main(flightradar_url=url)
        print("Scraping successfully finished")
        print(f"Please wait, script fell asleep for {minutes} minutes")
        sleep(minutes * 60)