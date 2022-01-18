import getpass
import argparse, os, time
import random
import selenium
from PDFMining import minePDFs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
from bs4 import SoupStrainer
from getpass import getpass
import pandas as pd
import re
import numpy as np
import sys, os, time
from datetime import datetime

print('Beginning Web Scraping')

'''
Used to normalise the company names
- Makes whole company name lower case
- Removes common company name parts that may disrupt search results
- Removes anything in brackets (and the brackets themselves)
- removes white space left in string
'''
def Normalise(companyName):
    normalisedName = companyName.lower()
    to_remove = ['\([^()]*\)','ltd', 'limited',' group','holdings',
                'llp','public','company','plc','united kingdom',
                'great britain','commercial','uk','.',';',
                ':','LLC','llc','holdings']
    normalisedName = re.sub("[\(\[].*?[\)\]]", "", normalisedName)
    for j in to_remove:
            normalisedName = normalisedName.replace(j, '')
    normalisedName.rstrip()
    normalisedName = " ".join(normalisedName.split())
    normalisedName = normalisedName.strip()
    return normalisedName

def SearchName(searchName,link,searchPhrase,afterDate,browser):
    browser.get(link)
    time.sleep(random.uniform(3, 4.9))
    try:
        button = browser.find_element_by_css_selector('#L2AGLb')
        ActionChains(browser).click(button).perform()
        print('Ready to Search')
    except:
        print('Ready to Search')
    #Search for given Criteria
    search = browser.find_element_by_name('q')
    search.send_keys(searchName+" "+searchPhrase+" filetype:pdf")
    search.send_keys(Keys.RETURN) # hit return after you enter search text


def WebScraper(companyNames,criteria,filePath,afterDate=''):
    noRelevantResults = []
    noRelevantResultsNorm = []
    #base link
    link = ('https://www.google.com/')
    #outputs to output report the search Criteria

    if afterDate == '':
        searchPhrase = criteria
    else:
        searchPhrase = criteria+" after:"+afterDate.strftime('%Y-%m-%d')+" filetype:pdf"
    file = open(filePath+'\\OutputReport.txt', 'a+')
    file.write('Search Term Used:')
    file.write('COPMANY NAME '+searchPhrase+'\n')
    file.close()
    time.sleep(random.uniform(3, 4.9)) # sleep for 5 seconds so you can see the results

    #for each company in csv
    for name in companyNames:
        normalisedName = Normalise(name)
        print('Original Name: ',name)
        print('Normalised Name: ',normalisedName)
        #generic download path
        downloadPath = filePath+'\\'+name+'\\Unfiltered'
        
        try:
            os.mkdir(filePath+'\\'+name)
        except FileExistsError:
            print('FOLDER ALREADY EXISTS')
        
        #Defining the webdriver. Set options so it can download PDFs
        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', {
        "download.default_directory": downloadPath, #Change default directory for downloads
        "download.prompt_for_download": False, #To auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
        })
        options.add_argument("start-maximized");
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        #browser = webdriver.Chrome(r"webDriver\chromedriver.exe",options=options)
        if getattr(sys, 'frozen', False): 
            #executed as a bundled exe, the driver is in the extracted folder
            chromedriver_path = os.path.join(sys._MEIPASS, "chromedriver.exe")
            browser = webdriver.Chrome(chromedriver_path,options=options)
        else:
            # executed as a simple script, the driver should be in `PATH`
            browser = webdriver.Chrome(options=options)

        time.sleep(random.uniform(3, 12.9))
        #searchName = '"'+normalisedName+'"'
        searchName = normalisedName
        SearchName(searchName,link,searchPhrase,afterDate,browser)

        #Take html of cite and find all links
        soup = bs(browser.page_source, features="html.parser")
        noMatchClassTags = soup.find_all("div", {"class": "v3jTId"})
        if noMatchClassTags:
            searchName = ' '.join('"{}"'.format(word) for word in normalisedName.split(' '))#adds qutation marks around each word
            SearchName(searchName,link,searchPhrase,afterDate,browser)
            soup = bs(browser.page_source, features="html.parser")
            noMatchClassTags = soup.find_all("div", {"class": "v3jTId"})

        if not noMatchClassTags:
            print('PDFs Found')
            #create folder for company
            try:
                os.mkdir(downloadPath)
            except FileExistsError:
                print('FOLDER ALREADY EXISTS: '+downloadPath)
                print(downloadPath)

            elems = browser.find_elements_by_xpath("//a[@href]")
            #for each link, if it ends in pdf, download it
            window_before = browser.window_handles[0]

            elemsPDF = []

            for elem in elems:
                if elem.get_attribute("href").endswith(('.pdf')):#If element is  pdf link
                    elemsPDF.append(elem)
            print(elemsPDF)
            for elem in elemsPDF[:1]:
                try:
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
            DTime = 0
            while wait and DTime<180:
                time.sleep(random.uniform(5, 7.9))
                wait = False
                for fname in os.listdir(downloadPath):
                    if fname.endswith('.crdownload'):
                        wait = True   
                downloadTime = time.time() - STime
                print(downloadTime)
            time.sleep(random.uniform(3, 4.9))

            minePDFs(filePath,name)

        else:
            os.rmdir(filePath+'\\'+name)
            noRelevantResults.append(name)
            noRelevantResultsNorm.append(normalisedName)
        
        

        browser.quit()
  

'''
CompanyNames = ['FACEBOOK']
criteria = 'scope 1 co2e'
downloadPath = r'F:\WebScraping\Temp'
#afterDate = datetime.fromtimestamp(1528797322)
afterDate = ''
starttime = time.time()
print(starttime)
WebScraper(CompanyNames,criteria,downloadPath,afterDate)
endtime = time.time()
print(endtime)
print(endtime - starttime)
time.sleep(5)
'''