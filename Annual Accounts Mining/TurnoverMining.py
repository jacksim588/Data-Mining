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
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
downloadPath = r'F:\WebScraping\Companies House co2\Bot Output\Downloads'
filteredPath = r'F:\WebScraping\Companies House co2\Bot Output\Filtered_Accounts'
'''
filterPhrases = ['comprehensive income',
                'income statement'
                'profit and loss account',
]
'''
filterPhrases = ['turnover',
                'revenue'
]
tempImagePath = r'F:\WebScraping\Companies House co2\Bot Output\Images'
os.mkdir(tempImagePath) 






'''
Filter PDF down to just pages with Co2 data
'''
for file in os.listdir(downloadPath):
    print('Starting Company: ',file)
    pages = convert_from_path(downloadPath+'\\'+file, 350)
    filteredPages = []
    print('Searching Pages for Account Data')
    print('Number of pages being searched: ', len(pages))
    pdf = FPDF()

    imageCount = 0
    for page in pages:
        imagePath = tempImagePath+'\\'+str(imageCount)+'.jpg'
        page.save(imagePath,'JPEG')
        image = cv2.imread(imagePath)
        text = str(pytesseract.image_to_string(image)).lower()

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
        outputFile = filteredPath+'\\'+file
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
        print('Exporting Filtered file')
        with open(outputFile, "wb") as outfile:
            output_writer.write(outfile)
        print('Filtered File Exported')
