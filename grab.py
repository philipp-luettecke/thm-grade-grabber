import sys
import configparser
from time import sleep
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import paho.mqtt.client as paho

URL = "https://studien-sb-service.th-mittelhessen.de/docu/online.html"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

config = configparser.ConfigParser()
print("Reading config.ini")
config.read("config.ini")

print("Refreshing data every " + str(int(config['GENERAL']['scan_interval'])) + " seconds")

def on_publish(client,userdata,result):
    print("data published \n")
    pass

mqtt_client = paho.Client("grader_publisher")

if (config['MQTT']['user']):
    mqtt_client.username_pw_set(config['MQTT']['user'], password=config['MQTT']['password'])

mqtt_client.on_publish = on_publish

while True:
    driver = webdriver.Chrome("chromedriver", options=chrome_options)
    driver.get(URL)

    try:

        driver.switch_to.frame(driver.find_element_by_name("inhalt"))
        username = driver.find_element_by_id("asdf")
        password = driver.find_element_by_id("fdsa")

        username.clear()
        username.send_keys(config['USERDATA']['user'])
        password.clear()
        password.send_keys(config['USERDATA']['password'])
        driver.find_element_by_name("submit").click()

        # navigate to Pruefungsverwaltung
        pruefungsverwaltung = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='makronavigation']/ul/li[3]/a")))
        pruefungsverwaltung.click()

        # navigate to Leistungsuebersicht
        driver.find_element_by_xpath("//*[@id='wrapper']/div[6]/div[2]/div/form/div/ul/li[4]/a").click()

        # navigate to Master of Science
        driver.find_element_by_xpath("//*[@id='wrapper']/div[6]/div[2]/form/ul/li/a[1]").click()

        # click on info for table view
        driver.find_element_by_xpath("//*[@id='wrapper']/div[6]/div[2]/form/ul/li/ul/li/a[1]").click()

        # get table and rows
        table = driver.find_element_by_xpath("//*[@id='wrapper']/div[6]/div[2]/form/table[2]")
        rows = table.find_elements(By.TAG_NAME, "tr")

        grades = {}
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > 6:
                #print(row.text)
                module = {
                    "number": cells[0].text,
                    "description": cells[1].text,
                    "semester": cells[2].text,
                    "grade": cells[3].text,
                    "percentage": cells[4].text,
                    "state": cells[5].text,
                    "credits": cells[6].text
                }
                grades[module['number']] = module
        #print(json.dumps(grades, indent=4, sort_keys=False))

        print("Connecting to " + config['MQTT']['host'] + ":" + str(int(config['MQTT']['port'])))
        mqtt_client.connect(config['MQTT']['host'],port=int(config['MQTT']['port']))
        print("Connected ... Publishing to " + config['MQTT']['topic'])
        ret = mqtt_client.publish(config['MQTT']['topic'], json.dumps(grades), retain=True)
        #print(ret)
        print("Disconnecting ...\r")
        mqtt_client.disconnect()
        print("Disconnected       ")
    finally:
        driver.quit()
        sleep(int(config['GENERAL']['scan_interval']))
