#!/usr/bin/python3
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import getpass
import sys
import page_elements
import time

target_url = "https://upassbc.translink.ca/"
target_url2 = "https://canvas.ubc.ca"

XPATH_UPASS = {"school_select": "//*[@class='hasCustomSelect']",
                "ubc": "//*[contains(@value, 'ubc')]",
                "ok": "//*[@id='goButton']",
                "checkbox": "//*[@id='goButton']",
                "request_pass": "//*[@id='requestButton']"}

XPATH_UBC = {"username_field": "//*[@id='username']",
                "password_field": "//*[@id='password']",
                "login": "//*[@id='_eventId_proceed']"}

app = Flask(__name__)
api = Api(app)


def setup_webdriver():
    driver = webdriver.Chrome()
    driver.get(target_url)
    return driver

def ubc_login(driver, username, password):
    username_field = driver.find_element_by_xpath(XPATH_UBC["username_field"])
    username_field.clear()
    username_field.send_keys(username)
    password_field = driver.find_element_by_xpath(XPATH_UBC["password_field"])
    password_field.clear()
    password_field.send_keys(password)
    driver.find_element_by_name("_eventId_proceed").click()
    #XPATH_UBC["login"]

def select_ubc_upass(driver):
    driver.find_element_by_xpath(XPATH_UPASS["school_select"]).click()
    driver.find_element_by_xpath(XPATH_UPASS["ubc"]).click()
    # element = driver.find_element_by_xpath("//*[@id='goButton']")
    # actions = ActionChains(driver)
    # actions.move_to_element(element).perform()
    time.sleep(2)
    driver.find_element_by_id("goButton").click()
    #XPATH_UPASS["ok"]

def request_ubc_upass(driver):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, XPATH_UPASS["checkbox"])))
    checkbox = driver.find_element_by_xpath(XPATH_UPASS["checkbox"])
    actions = ActionChains(driver)
    actions.move_to_element(checkbox).perform()
    checkbox.click()
    driver.find_element_by_xpath(XPATH_UPASS["request_pass"]).click()

def request_script():
    ubc_username = ''
    ubc_password = ''
    driver = setup_webdriver()
    select_ubc_upass(driver)
    ubc_login(driver, ubc_username, ubc_password)
    # request_ubc_upass(driver)
    return "200"



@app.route('/autopass', methods=['GET'])
def autopass():
    try:
        request_script()
    except:
        return "there was an error"
    else:
        return "UPass requested successfully"



if __name__ == '__main__':
     app.run(debug=True)
