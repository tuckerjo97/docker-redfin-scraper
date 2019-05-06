import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import time
import requests
import sys
import io
import random
from lxml.html import fromstring

def generate_zip_urls():
    # Generates URLs for scrapper to run through. URLs are based off California zip codes downloaded from:
    # https://www.unitedstateszipcodes.org/zip-code-database/
    # ZIPCODEs are then formatted into Redfin URLs with the format:
    # https://www.redfin.com/zipcode/ZIPCODE/filter/include=sold-3mo

    zip_df = pd.read_csv('formatted_zip.csv')
    formatted_url = pd.DataFrame(zip_df['zip_code'].apply(lambda x: "https://www.redfin.com/zipcode/%d/filter/include=sold-3mo" % x))
    formatted_url['original_zip'] = zip_df['zip_code']
    return formatted_url

def pull_csv_get(driver, url):
    # Formats a get request for the given zipcode in order to pull housing data for that zipcode. Need to change the
    # num_homes parameter or else will only get 350 homes

    driver.get(url)
    download = driver.find_element_by_id('download-and-save').get_attribute('href')
    download = download.split('num_homes=')
    temp = download[1].split('&', 1)
    final = download[0] + 'num_homes=' + '5000' + '&' + temp[1]
    return final

def get_request_handler(url, zip):
    # Formats get request and converts response into csv, which is then saved as ZIPCODE.csv

    HEADER = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)' \
                      ' Chrome/49.0.2623.112 Safari/537.36'
    }
    url, param = url.split("?")
    param = param.split('&')
    param_dict = {}
    for p in param:
        k,v = p.split('=')
        param_dict[k] = str(v)
    r = requests.get(url=url, params=param_dict, headers=HEADER).content
    data = pd.read_csv(io.StringIO(r.decode('utf-8')))
    print(zip, ' len:', len(data))
    name = 'data/' + str(zip) +'.csv'
    data.to_csv(path_or_buf=name)
    return data

def append_master_file(data, n):
    # appends data to master file keeping track of indexes
    len_data = len(data)
    data.index = range(n, n+len_data)
    with open('data/master_file.csv', 'a') as f:
        data.to_csv(f, header=False)
        print('master file appended')
    n = n+len_data
    return n

if __name__ == '__main__':
    # Generates blank master file
    master_file = open('data/master_file.csv', 'w')
    master_file.write('index,SALE TYPE,SOLD DATE,PROPERTY TYPE,ADDRESS,CITY,STATE OR PROVINCE,ZIP OR POSTAL CODE,PRICE,BEDS,BATHS,LOCATION,SQUARE FEET,LOT SIZE,YEAR BUILT,DAYS ON MARKET,$/SQUARE FEET,HOA/MONTH,STATUS,NEXT OPEN HOUSE START TIME,NEXT OPEN HOUSE END TIME,URL (SEE http://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING),SOURCE,MLS#,FAVORITE,INTERESTED,LATITUDE,LONGITUDE\n')
    master_file.close()

    # Set up URLs for every zip code in california
    zip_urls_df = generate_zip_urls()
    print("zip codes formatted")

    # Set up headless selenium web driver
    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    # Generates GET request, pulls CSV, formats csv
    failed_codes = []
    len_master = 0
    for _, zip_url in zip_urls_df.iterrows():
        try:
            print("attempting zip: ", str(zip_url[1]))
            get_request_url = pull_csv_get(driver, zip_url[0])
            data = get_request_handler(get_request_url, zip_url[1])
        except:
            print(str(zip_url[1]), 'has FAILED')
            failed_codes.append(zip_url[1])
            continue
        len_master = append_master_file(data, len_master)
        time.sleep(random.randint(5, 10))
    failed_codes = pd.Series(failed_codes)
    failed_codes.to_csv(path_or_buf='data/failed.csv', header=['failed_zip'])
    print(pd.read_csv('data/master_file.csv').head())
    driver.quit()
