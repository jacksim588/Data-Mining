import cv2
import os
import pytesseract
from PIL import Image
import numpy as np
import pandas as pd
import shutil

from pdf2image import convert_from_path

#Tesseract exe is stored in as PATH variable. could be an issue when using on Virtual Machine
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


tempImagePath = r'F:\WebScraping\Companies House co2\Bot Output\Images'
downloadPath = r'F:\WebScraping\Companies House co2\Bot Output\Test Downloads'
filteredPath = r'F:\WebScraping\Companies House co2\Bot Output\Test Filtered Accounts'
filterPhrases = ['turnover',
                'revenue'
]

#If the image folder exists, remove all files in it. If it doesn't, create an empty folder
if os.path.exists(tempImagePath) and os.path.isdir(tempImagePath):
    shutil.rmtree(tempImagePath)
os.mkdir(tempImagePath)
'''
Function which, when given a list of numbers, 
returns a list of number pairs representing concurrent numbers
'''
def ranges(data):
    data = sorted(set(data))
    gaps = [[s, e] for s, e in zip(data, data[1:]) if s+1 < e]
    edges = iter(data[:1] + sum(gaps, []) + data[-1:])
    return list(zip(edges, edges))
'''
Function which, given a string, splits into an list using " " as the deliminator
'''
def toList(string):
    li = list(string.split(" "))
    return li


'''
Cycles for each File in the downloads folder, so that it covers each pdf.
Can be changed to be within a loop which downloads the PDFs
To do that, need to replace 'for each file' with 'latest file'
'''

#unfilteredPDFPath = max(listOfFiles, key=os.path.getctime) #Get latest file
for unfilteredPDFPath in os.listdir(downloadPath):
    filteredPages = [] #list to hold pages with relevant key words

    pages = convert_from_path(downloadPath+'\\'+unfilteredPDFPath, 350) #converts a PDF to a list of images

    #Useful for bug testing, can be commented out
    print('Searching Pages for Data')
    print('Number of pages being searched: ', len(pages))

    imageCount = 0 #cv2 requires an image path, so the image is stored locally using image count as name
    cumulateArray = [] #Stores the extracted Data from the filtered PDF Pages
    for page in pages:
        imagePath = tempImagePath+'\\'+str(imageCount)+'.jpg'
        page.save(imagePath,'JPEG') #saves image as jpeg to temp storage
        image = cv2.imread(imagePath) #imports image as cv2 image object
        text = str(pytesseract.image_to_string(image)).lower() #Uses OCR to extract text (as lower case) from the page as a string
        if any(word in text for word in filterPhrases): #if any of the filtered phrases are in the page
            print('Data found in page')
            blankrow = [255]*len(image[:, :, 0][0]) #create a blank image of the same dimensions
            '''
            Goes through each pixel for each line in the image.
            A line is appended to 'datainrow' if any of its pixels have a value of less than 200
            Values range from 0-255, with 0 being complete black, and 255 being complete white
            This creates a list of pixel rows from the image which contain text
            '''
            #REPALCE THIS WITH THE FUNCTION IN THE IPYNB
            datainrow = [] 
            i=0
            for line in image[:, :, 0]:
                if all(i >= 200 for i in line):
                    #print('empty')
                    pass
                else:
                    #print('found')
                    datainrow.append(i)
                i=i+1
            '''
            Gets a list of pairs of numbers. 
            each pair represents a set of concurrent rows where data is found
            this used to extract each line data from the image
            '''
            dataRanges = (ranges(datainrow))

            
            for foundData in dataRanges:
                currentImage = []
                rangeList = list(foundData)

                if rangeList[1] - rangeList[0] > 1: #if there is more than 1 consecutive row with data
                    #adds buffer to lower bound
                    if rangeList[0] >=2:
                        lowerBound = rangeList[0]-2
                    else:
                        lowerBound = 0
                    #adds buffer to upper bound
                    if rangeList[1] < len(image[:, :, 0])-3:
                        upperBound = rangeList[1]+3
                    else:
                        upperBound = len(image[:, :, 0])
                    
                    #uses bounds to create image of current selection
                    for i in range(lowerBound,upperBound):
                        #print(i)
                        currentImage.append(image[:, :, 0][i])
                    '''
                    Exports current data row as image
                    Need to do this as, the function to create a cv2 image object, needed to use OCR,
                    requires a filepath, rather than passing a variable
                    '''
                    currentImage = np.asarray(currentImage)
                    im = Image.fromarray(currentImage)
                    '''
                    TODO Import currentImage into a a temporary, local, folder
                    '''
                    im.save(str(foundData)+"your_file.jpeg")
                    dataRowImage = cv2.imread(str(foundData)+"your_file.jpeg")
                    
                    '''
                    Extracts text from the dataRowImage
                    Converts text into an array of each block of words
                    The data we are looking for, will always have the last two words as the numbers, and the rest as the label
                    Therefore, the last two words are extracted into y0, and y1, and the rest are extracted into a label variable
                    These are then appended to a dataframe for the current PDF.
                    This dataframe can then be manipulated to create an csv
            
                    '''
                    text = str(pytesseract.image_to_string(dataRowImage)).rstrip()
                    textArray = toList(text.rstrip("\n"))
                    if len(textArray) >=3:
                        y0 = textArray[-2]
                        y1 = textArray[-1]
                        label = ' '.join(textArray[:-1])
                        outputArray = [label,y0,y1]
                        #print(outputArray)
                        cumulateArray.append(outputArray)

    '''
    Creates dataframe from extracted data data
    3 columns: label, y0 and y1
    y1 = last word in row
    y0 = second to last word in row
    label = the rest of the row

    regex is used to filter the y0, and y1, columns down to just numbers
    in the format we want
    '''
    print(cumulateArray)
    df = pd.DataFrame(cumulateArray)
    print(df)
    df.columns = ['Label','Y0','Y1']
    print(df)
    df = df.replace('\n','', regex=True)
    df['Y1'] = df['Y1'].replace(r'[^0-9()^.]','', regex=True)
    df['Y0'] = df['Y0'].replace(r'[^0-9()^.]','', regex=True)
    


    df['Y0'] = df['Y0'].replace(['.','(',')','()'],None)
    df['Y1'] = df['Y1'].replace(['.','(',')','()'],None)
    df = df.dropna(subset=['Y0', 'Y1'], how='all')
    #df = df[(df.Y0 != '')or(df.Y1 != '')]
    print(df)
    df.to_csv('example.csv',index=False) 