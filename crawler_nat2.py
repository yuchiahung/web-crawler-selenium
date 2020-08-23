## crawler nat.gov.tw
## 爬取經濟部商業司 商工登記公示資料查詢服務

## 參考：https://medium.com/datainpoint/python-essentials-web-scraping-with-selenium-638175f839ee

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import numpy as np
import random

def get_company_info_from_url(htmltext):
    """get companies' info from html text: 地址 統編 資本額 實收資本額 """
    soup = BeautifulSoup(htmltext)
    info_title = ['公司名稱', '公司所在地', '統一編號', '資本總額(元)', '實收資本額(元)']
    info = []
    for title in info_title:
        try:
            value = soup.find('td',string = title, class_='txt_td').find_next_siblings('td')[0].text.strip()
            info.append(re.sub(r"\s+", "", value).replace(',', ''))
        except:
            info.append(np.nan)
    # address
    info[1] = info[1][:-4]
    # tax_id
    info[2] = info[2][:-2]
    return info



def get_company_info(name_list):
    """get companies' info from companies' names"""
    # options = Options()
    # options.add_argument("--disable-notifications")
    chrome = webdriver.Chrome('./chromedriver')
    # , chrome_options=options)
    companies = dict() 
    for name in name_list:
        chrome.get("https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do")
        # enter the name
        search_input = chrome.find_element_by_name("qryCond")
        search_input.send_keys(name)
        # click the 'search' button
        time.sleep(random.uniform(2, 4)) # 限制兩秒鐘後才能查詢
        start_search_btn = chrome.find_element_by_id("qryBtn")
        start_search_btn.click()
        time.sleep(random.uniform(2, 4))
        # click the first result
        try:
            first_result_elem = chrome.find_element_by_xpath("//div[@class='panel panel-default'][1]/div[@class='panel-heading companyName']/a[@class='hover']")
            first_result_elem.click()
        # get the html text from this company's info page
            htmltext = chrome.page_source
            company_info = get_company_info_from_url(htmltext)
            companies[name] = company_info
        except:
            companies[name] = [np.nan, np.nan, np.nan, np.nan, np.nan]
    chrome.close()
    return companies

company_name_list = ['統一有限公司', '鴻海精密工業股份有限公司', '大立光電股份有限公司', '台灣積體電路製造股份有限公司', '中國信託商業銀行股份有限公司']
company_info_df = pd.DataFrame.from_dict(get_company_info(company_name_list), orient='index')
company_info_df.columns = ['name', 'address', 'tax_id', 'capital', 'paid_in_cap']

company_info_df.to_csv('output/company_info_df.csv', encoding='utf_8_sig')



