import getpass
import argparse, os, time
import random
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
from bs4 import SoupStrainer
from getpass import getpass
import os
import pandas as pd
import re
import numpy as np
import time


'''
Runs for each name in the company names list
Creates a new browser object each time so the download location can be changed
this allows each company pdfs to be downloaded in the same folder.
'''
def Normalise(CompanyNames):
    normalised_names = []
    CompanyNames = [x.lower() for x in CompanyNames]
    to_remove = ['\([^()]*\)','ltd', 'limited',' group','holdings','llp','public','company','plc','united kingdom','great britain','commercial','uk','.',';',':']
    for i in CompanyNames:
        for j in to_remove:
            i = i.replace(j, '')
        i.rstrip()
        normalised_names.append(i)
    normalised_names = [x.rstrip() for x in normalised_names]
    return normalised_names




def WebScraper(companyNames,Criteria,downloadPath,AfterDate):
    CompanyNames = Normalise(companyNames)
    criteria = Criteria
    downloadPath = downloadPath
    link = ('https://www.google.com/')
    file = open(downloadPath+'\\OutputReport.txt', 'a+')
    file.write(criteria+" after:"+AfterDate.strftime('%Y-%m-%d')+" filetype:pdf"+'\n')
    file.close()
    for name in CompanyNames:
        #create folder for PDFs to go in
        filepath = downloadPath+'\\'+name
        
        #Defining the webdriver. Set options so it can download PDFs
        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', {
        "download.default_directory": filepath, #Change default directory for downloads
        "download.prompt_for_download": False, #To auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
        })
        options.add_argument("start-maximized");
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        browser = webdriver.Chrome(r"C:\webdrivers\chromedriver.exe",options=options)
        time.sleep(random.uniform(3, 12.9))

        #Load Google
        browser.get(link)
        time.sleep(random.uniform(3, 4.9))
        button = browser.find_element_by_css_selector('#L2AGLb')
        ActionChains(browser).click(button).perform()
        
        #Search for given Criteria
        search = browser.find_element_by_name('q')
        exc_name = ' '.join('"{}"'.format(word) for word in name.split(' '))#adds qutation marks around each word
        exc_name = re.sub("[\(\[].*?[\)\]]", "", exc_name)
        search.send_keys(exc_name+" "+criteria+" after:"+AfterDate.strftime('%Y-%m-%d')+" filetype:pdf")
        search.send_keys(Keys.RETURN) # hit return after you enter search text

        time.sleep(random.uniform(3, 4.9)) # sleep for 5 seconds so you can see the results



        #Take html of cite and find all links
        soup = bs(browser.page_source, features="html.parser")

        noMatchClassTags = soup.find_all("div", {"class": "v3jTId"})
        print(noMatchClassTags)

        elems = browser.find_elements_by_xpath("//a[@href]")
        #if there is not 'no matches' message, carry on as normal
        if not noMatchClassTags:
            #create folder for company
            try:
                os.mkdir(filepath)
            except FileExistsError:
                print('FOLDER ALREADY EXISTS: '+filepath)
                print(filepath)
            #for each link, if it ends in pdf, download it
            window_before = browser.window_handles[0] 

            for elem in elems:
                try:
                    if elem.get_attribute("href").endswith(('.pdf')):#If element is  pdf link
                        pdflink = elem.get_attribute("href")#get link
                        browser.execute_script("window.open('{}');".format(''))#open blank tab
                        window_after = browser.window_handles[1]
                        browser.switch_to.window(window_after)#swap to new tab
                        browser.get(pdflink)#search pdf link (if its a pdf it will autodownload)
                        browser.close()#close tab
                        browser.switch_to.window(window_before)#swap back to original tab
                except (selenium.common.exceptions.StaleElementReferenceException,selenium.common.exceptions.WebDriverException):
                    print('StaleElementReferenceException')

            #Wait to make sure each pdf is downloaded before continuing
            wait = True
            STime = time.time()
            downloadTime = 0
            while wait and downloadTime<180:
                time.sleep(random.uniform(5, 7.9))
                wait = False
                for fname in os.listdir(filepath):
                    if fname.endswith('.crdownload'):
                        wait = True   
                downloadTime = time.time() - STime
                print(downloadTime)
            time.sleep(random.uniform(3, 4.9))
            #print('moving on from ',name)
        else:
            file = open(downloadPath+'\\OutputReport.txt', 'a+')
            file.write(name+'\n')
            file.close()
        browser.quit()

        '''
        This is where the filter process could go.
        Make another function which takes the directory and filters all the PDFs in its
        '''

'''
CompanyNames = ['ABACO RECRUITMENT LIMITED','ASDA','ABACO RECRUITMENT LIMITED']
criteria = 'scope 1 co2e'
downloadPath = r'F:\Webscraping\Downloads'


starttime = time.time()
print(starttime)
WebScraper(CompanyNames,criteria,downloadPath)
endtime = time.time()
print(endtime)
print(endtime - starttime)
time.sleep(5)
'''