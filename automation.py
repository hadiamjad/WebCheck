from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import shutil

import pandas as pd
import requests
import os




# selenium to visit website and get logs
def visitWebsite(df):
    # extension filepath
    ext_file = "C:/Users/Hadiy/Downloads/clicks-extension/extension"

    opt = webdriver.ChromeOptions()
    # devtools necessary for complete network stack capture
    opt.add_argument("--auto-open-devtools-for-tabs")
    # loads extension
    opt.add_argument("load-extension=" + ext_file)
    # important for linux
    opt.add_argument("--no-sandbox")
    opt.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opt)
    driver.get(r"https://" + df["website"][i])

    # sleep
    time.sleep(50)

    driver.quit()


df = pd.DataFrame([["soccerstreams100.io"]], columns=["website"])

for i in df.index:
    # visit website
    visitWebsite(df)
