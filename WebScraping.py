#import subprocess
#import sys

#def install(package):
#    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

#install("selenium")
#install("bs4")
#install("webdriver-manager")

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

# selenium 4
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager



options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

def extractTextFromLink(site):
    #site = 'https://policies.google.com/terms?hl=en'

    wd = webdriver.Chrome('D:\\BSCS 3-3\\Second Semester\\6 CS Thesis Writing 1\\Project (Software)\\ToSUM V1 - Copy\\chromedriver',options=options)
    wd.get(site)

    html = wd.page_source

    from selenium.webdriver.common.keys import Keys

    from selenium.webdriver.common.by import By
    element = wd.find_element(By.TAG_NAME,"Body")
    with open('D:\\BSCS 3-3\\Second Semester\\6 CS Thesis Writing 1\\Project (Software)\\ToSUM V1 - Copy\\scraped.txt', 'w', encoding="utf-8") as f:
        f.write(element.text)

    return element.text