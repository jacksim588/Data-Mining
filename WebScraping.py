import getpass
import argparse, os, time
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
from bs4 import SoupStrainer
from getpass import getpass
import os
import pandas as pd
import re
import numpy as np

CompanyNames = ['NEXT','greene king']
link = ('https://www.google.com/')
criteria = 'co2e'

'''
Runs for each name in the company names list
Creates a new browser object each time so the download location can be changed
this allows each company pdfs to be downloaded in the same folder.
'''
for name in CompanyNames:
    #create folder for PDFs to go in
    filepath = r'F:\Downloads'+'\\'+name
    try:
        os.mkdir(filepath)
    except FileExistsError:
        print('FOLDER ALREADY EXISTS: '+filepath)
    print(filepath)
    #Defining the webdriver. Set options so it can download PDFs
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {
    "download.default_directory": filepath, #Change default directory for downloads
    "download.prompt_for_download": False, #To auto download the file
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
    })
    browser = webdriver.Chrome(r"C:\webdrivers\chromedriver.exe",options=options)
    time.sleep(random.uniform(3, 4.9))

    #Load Google
    browser.get(link)
    time.sleep(random.uniform(3, 4.9))

    #Search for given Criteria
    search = browser.find_element_by_name('q')
    search.send_keys(name+" "+criteria+" filetype:pdf")
    search.send_keys(Keys.RETURN) # hit return after you enter search text
    time.sleep(5) # sleep for 5 seconds so you can see the results

    #Take html of cite and find all links
    soup = bs(browser.page_source, features="html.parser")
    elems = browser.find_elements_by_xpath("//a[@href]")
    #for each link, if it ends in pdf, download it
    for elem in elems:
        if elem.get_attribute("href").endswith(('.pdf')):
            #print(elem.get_attribute("href"))
            browser.get(elem.get_attribute("href"))
    #Wait to make sure each pdf is downloaded before continuing
    wait = True
    while wait == True:
        time.sleep(random.uniform(5, 7.9))
        wait = False
        for fname in os.listdir(filepath):
            if fname.endswith('.crdownload'):
                wait = True
        
    time.sleep(random.uniform(3, 4.9))
    browser.quit()

time.sleep(5)