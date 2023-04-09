from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import time

# from pyvirtualdisplay import Display
import pandas as pd
import requests
import os
import json


# virtual display
# display = Display(visible=0, size=(800, 600))
# display.start()

df = pd.read_csv(r"test.csv")

for i in df.index:
    # try:
        if i < 0:
            pass
        else:
            dic = {}
            # extension filepath
            ext_file = "extension"

            opt = webdriver.ChromeOptions()
            # devtools necessary for complete network stack capture
            opt.add_argument("--auto-open-devtools-for-tabs")
            # # loads extension
            opt.add_argument("load-extension=" + ext_file)
            # important for linux
            opt.add_argument("--no-sandbox")
            opt.add_argument("--disable-dev-shm-usage")
            
            # Enable 3rd party cookie blocking or allow all cookies
            # prefs = {"profile.cookie_controls_mode": 1, "profile.default_content_setting_values.cookies": 0}
            prefs = {"profile.cookie_controls_mode": 0}
            opt.add_experimental_option("prefs", prefs)
 
            dc = DesiredCapabilities.CHROME
            dc["goog:loggingPrefs"] = {"browser": "ALL"}

            os.mkdir("server/output/" + df["website"][i])
            driver = webdriver.Chrome(
                ChromeDriverManager().install(), options=opt, desired_capabilities=dc
            )
            requests.post(
                url="http://localhost:3000/complete", data={"website": df["website"][i]}
            )
            driver.get(r"https://www." + df["website"][i])

            time.sleep(2000)

            cookies = driver.get_cookies()
            print(cookies)
            # Save cookies to a JSON file
            with open('server/output/' + df["website"][i]+'/cookies_table_after_crawl.json', 'w') as f:
                json.dump(cookies, f)
            driver.delete_all_cookies()
            # driver.quit
            driver.quit()
    # except Exception as e:
    #     print(r'exception:', e)
    #     try:
    #         driver.quit()
    #     except:
    #         pass
    #     print(r"Crashed: " + str(i) + " website: " + df["website"][i])