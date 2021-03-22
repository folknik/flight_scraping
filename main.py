import os
import json
import psycopg2
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from typing import Dict


minutes = float(os.environ['minutes'])

with open("./credentials.json", "r+") as f:
    refs = json.loads(f.read())


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


def insert_data(aircrafts_table, flights_table):
    conn = psycopg2.connect(dbname=refs["postgres_db"],
                            user=refs["postgres_user"],
                            password=refs["postgres_pw"],
                            host=refs["postgres_host"])
    cursor = conn.cursor()

    for line in aircrafts_table:
        query = """ SELECT hexident FROM public.aircrafts_scraping 
                    WHERE hexident = '{}' fetch first 1 rows only""".format(line[0])
        cursor.execute(query)
        record = cursor.fetchone()

        if record is None:
            insert_query = """ INSERT INTO public.aircrafts_scraping (hexident, type, registration) 
                               VALUES (%s,%s,%s) """
            cursor.execute(insert_query, line)
            conn.commit()

    for line in flights_table:
        query = """ SELECT callsign_2 FROM public.flights_scraping 
                    WHERE callsign_2 = '{}' fetch first 1 rows only""".format(line[3])
        cursor.execute(query)
        record = cursor.fetchone()

        if record is None:
            insert_query = """ INSERT INTO public.flights_scraping (from_airport, to_airport,
                                            callsign_1, callsign_2, operator)
                               VALUES (%s,%s,%s,%s,%s) """
            cursor.execute(insert_query, line)
            conn.commit()

    cursor.close()


def process_data(data: Dict[str, str]) -> None:
    aircrafts = []
    flights = []
    for key in data.keys():
        if isinstance(data[key], list):
            content = data[key]
            hexident, aircraft_type, registration = content[0], content[8], content[9]
            from_airport, to_airport = content[11], content[12]
            callsign_1, callsign_2, operator = content[13], content[16], content[18]
            if hexident and aircraft_type and (from_airport or to_airport):
                aircrafts.append((hexident, aircraft_type, registration))
                flights.append((from_airport, to_airport, callsign_1, callsign_2, operator))
    insert_data(aircrafts, flights)


def main() -> None:
    urls = {
        'Moscow': refs['moscow_url'],
        'Omsk': refs['omsk_url']
    }
    while True:
        driver = webdriver.Chrome('/usr/bin/google-chrome', options=set_chrome_options())
        try:
            while True:
                print(f"\n\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, scraping has started")
                for city in urls.keys():
                    driver.get(urls[city])
                    contents = json.loads(driver.find_element_by_tag_name('pre').text)
                    process_data(contents)
                    print("Scraping successfully finished for {}".format(city))
                print(f"Please wait, script fell asleep for {minutes} minutes")
                driver.close()
                sleep(minutes * 60)
        except Exception as e:
            driver.close()
            driver.quit()
            sleep(5 * 60)


if __name__ == '__main__':
    main()