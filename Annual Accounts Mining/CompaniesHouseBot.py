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
import pandas as pd
import re
import glob
import os
import numpy as np
import sys, os, time
from datetime import datetime
import cv2
import pdf2image
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from fpdf import FPDF
from PyPDF4 import PdfFileReader, PdfFileWriter

downloadPath = r'F:\WebScraping\Companies House co2\Bot Output\Downloads'
filteredPath = r'F:\WebScraping\Companies House co2\Bot Output\Filtered'
tempImagePath = r'F:\WebScraping\Companies House co2\Bot Output\Images'
os.mkdir(tempImagePath) 
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
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

if getattr(sys, 'frozen', False): 
    #executed as a bundled exe, the driver is in the extracted folder
    chromedriver_path = os.path.join(sys._MEIPASS, "chromedriver.exe")
    browser = webdriver.Chrome(chromedriver_path,options=options)
else:
    # executed as a simple script, the driver should be in `PATH`
    browser = webdriver.Chrome(options=options)

time.sleep(random.uniform(3, 12.9))

df = pd.read_csv (r'F:\WebScraping\Companies House co2\Copy of Jack 800 test(10681) temp.csv', encoding = "ISO-8859-1")
companyNumbers = df['Registered number'].tolist()
firstCompany = True
filterPhrases = [
    'Scope 1',
    'Scope 2',
    'Scope 3',
    'scope 1',
    'scope 2',
    'scope 3',
    'CO2',
    'GHG',
    'ghg'
]
for companyNumber in companyNumbers:
    '''
    Download latest company accounts file for each file in companyNumbers List
    '''
    try:
        browser.get('https://find-and-update.company-information.service.gov.uk/company/'+companyNumber.zfill(8)+'/filing-history')
        time.sleep(random.uniform(3, 12.9))
        if firstCompany:
            browser.find_element_by_id('filter-category-accounts').click()
        #elems = browser.find_element_by_id('fhTable').find_elements_by_xpath("//a[@href]")
        elems = browser.find_elements_by_class_name('download')
        files = []
        for elem in elems:  
            print(elem.get_attribute("href"))
        elems[0].click()
        firstCompany = False
        time.sleep(random.uniform(3, 4.7))
        '''
        Deals with Bad gateway by waiting and repeating
        '''
    except IndexError: 
        time.sleep(random.uniform(20, 25))
        browser.get('https://find-and-update.company-information.service.gov.uk/company/'+companyNumber.zfill(8)+'/filing-history')
        time.sleep(random.uniform(3, 12.9))
        if firstCompany:
            browser.find_element_by_id('filter-category-accounts').click()
        #elems = browser.find_element_by_id('fhTable').find_elements_by_xpath("//a[@href]")
        elems = browser.find_elements_by_class_name('download')
        files = []
        for elem in elems:  
            print(elem.get_attribute("href"))
        elems[0].click()
        firstCompany = False
    '''
    Rename File to the company Number
    '''
    listOfFiles = glob.glob(downloadPath+'/*') # * means all if need specific format then *.csv
    latestFile = max(listOfFiles, key=os.path.getctime)
    outputFileName = companyNumber+'.pdf'
    os.rename(latestFile,downloadPath+'\\'+outputFileName)
    time.sleep(random.uniform(1, 2))

    '''
    Filter PDF down to just pages with Co2 data
    '''
    pages = convert_from_path(downloadPath+'\\'+outputFileName, 350)
    filteredPages = []
    print('Searching Pages for CO2 Data')
    print('Number of pages being searched: ', len(pages))
    pdf = FPDF()
    
    imageCount = 0
    for page in pages:
        imagePath = tempImagePath+'\\'+str(imageCount)+'.jpg'
        page.save(imagePath,'JPEG')
        image = cv2.imread(imagePath)
        text = str(pytesseract.image_to_string(image))
        if any(word in text for word in filterPhrases):
            filteredPages.append(image)
            print('Data found in Page')
            #image.save("out.jpg")
            #page.save('out.jpg','JPEG')
            pdf.add_page()
            #print(page)
            pdf.image(imagePath,x = None, y = None, w = 210, h = 297, type = '', link = '')
            imageCount+=1
    '''
    Export Filtered pages to PDF
    '''
    if not filteredPages:
        print('No Co2 Data found')
    else:
        print('Co2 Data Found')
        print('Number of pages with Co2 Data: ',len(filteredPages))
        '''
        pdf = FPDF()
        for page in filteredPages:
            image = Image.fromarray(page)
            image.save("out.jpg")
            #page.save('out.jpg','JPEG')
            pdf.add_page()
            #print(page)
            pdf.image('out.jpg',x = None, y = None, w = 210, h = 297, type = '', link = '')
        '''
        outputFile = filteredPath+'\\'+outputFileName
        pdf.output(outputFile, "F")
        print('FILE EXPORTED CHECK')
        time.sleep(random.uniform(30, 40.7))
        '''
        The way the image is exported to a PDF, for each page a redundant blank page is produced (the create the PDF in the first place)
        This is an are to improve, and is fixed in the following section which is inefficient
        '''
        number_of_pages = len(filteredPages*2)
        print('Number of Pages in PDF (including blank pages): ',number_of_pages)
        output_writer = PdfFileWriter()
        pdfOne = PdfFileReader(outputFile)
        for i in list(range(0, number_of_pages)):
            print(i)
            if i % 2 != 0:
                print('using page')
                page = pdfOne.getPage(i)
                output_writer.addPage(page)
        print('Number of Pages in PDF (excluding blank pages): ',number_of_pages)
        with open(outputFile, "wb") as outfile:
            output_writer.write(outfile)
os.rmdir(tempImagePath) 