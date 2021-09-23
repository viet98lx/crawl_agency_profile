import json
import os.path
import re
import time
import traceback
import logging
from pythonjsonlogger import jsonlogger
import pandas as pd
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.DEBUG, filemode='a')
logger = logging.getLogger(__name__)
formatter = jsonlogger.JsonFormatter(json_ensure_ascii=False)
fileHandler = logging.FileHandler("crawl_agency_info.log")
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logHandler = logging.StreamHandler(sys.stdout)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# init
path = '/home/viet/chromedriver_linux64/chromedriver'
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.headless = True
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36")
driver = webdriver.Chrome(executable_path=path, options=chrome_options)

def test():
    driver.get('https://alomuabannhadat.vn/tim-moi-gioi/1-0/0/')
    time.sleep(2)
    arr_link = driver.find_elements_by_class_name("agent")
    print(len(arr_link))
    data_agency = [x.text for x in arr_link]
    print(data_agency)

def parse_page_agency(provinces_nb,page_nb):
    if page_nb == 1:
        link = 'https://alomuabannhadat.vn/tim-moi-gioi/{}-0/0/'.format(provinces_nb)
    else:
        link = 'https://alomuabannhadat.vn/tim-moi-gioi/{}-0/0/page-{}'.format(provinces_nb, page_nb)
    driver.get(link)
    time.sleep(2)
    arr_link = driver.find_elements_by_class_name("agent")
    data_agency = [parse_info_agency(x.text) for x in arr_link]
    logger.info("parse done {} in page {}".format(str(len(arr_link)), link))
    return data_agency

def parse_info_agency(info_string):
    elements = re.split('\n', info_string)
    agency_info = {}
    agency_info['name'] = elements[0]
    for element in elements:
        if re.match(r'\d+',element):
            agency_info['phone'] = element
            continue
        if re.match(r'.*@.*\.com',element):
            agency_info['email'] = element
    return agency_info

if __name__ == '__main__':
    provinces_page_nb = [1]
    max_detail_pages_nb = 3
    for province_nb in provinces_page_nb:
        for page_nb in range(1,max_detail_pages_nb):
            try:
                list_agency_info = parse_page_agency(province_nb, page_nb)
                if not os.path.exists('agency_info.json'):
                    with open('agency_info.json', 'w') as f:
                        json.dump(list_agency_info, f, ensure_ascii=False, indent=4)
                else:
                    with open('agency_info.json') as f:
                        old_list = json.load(f)
                    new_list = old_list + list_agency_info
                    with open('agency_info.json', 'w') as f:
                        json.dump(new_list, f, ensure_ascii=False, indent=4)
            except:
                error_msg = traceback.format_exc()
                error_obj = {
                    "time": str(datetime.fromtimestamp(time.time())),
                    "error": error_msg
                }
                logger.error("error parse province nb {} at page: {}".format(province_nb,page_nb), extra=error_obj)
                continue

            time.sleep(0.01)


