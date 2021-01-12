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
    while True:
        main(web_url=url)
        print("Scraping successfully finished")
        print(f"Please wait, script fell asleep for {minutes} minutes")
        sleep(minutes * 60)