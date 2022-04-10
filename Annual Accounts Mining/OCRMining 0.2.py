import cv2
import csv
import os
import pytesseract
from PIL import Image
import numpy as np
import pandas as pd
import shutil
import numpy as np
from pathlib import Path
from pdf2image import convert_from_path
import time

from sklearn.model_selection import StratifiedShuffleSplit
print('Beginning')
#Tesseract exe is stored in as PATH variable. could be an issue when using on Virtual Machine
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
poppler_path = r"C:\Program Files\poppler-0.68.0\bin"

'''
tempImagePath = r'F:\WebScraping\Companies House co2\Bot Output\Images'
downloadPath = r'F:\WebScraping\Companies House co2\Bot Output\Test Downloads'
filteredPath = r'F:\WebScraping\Companies House co2\Bot Output\Test Filtered Accounts'
'''

mainFolder = r'C:\Users\Clamfighter\Documents\GitHub\Data-Mining\Data-Mining\Bot Output'
tempImagePath = mainFolder+ '\\bin'
downloadPath = mainFolder+ '\downloads'
filteredPath = mainFolder+ '\Test Filtered Accounts'
outputfilePath = 'output(temp).csv'

filterPhrases = ['gross profit'
]


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

def getDataRangesFromImage(imageArray):
    datainrow = []
    #print(len(imageArray))
    i=0
    for line in imageArray:
        #print(line)
        if all(i >= 200 for i in line):
            #print('empty')
            pass
        else:
            #print('found')
            datainrow.append(i)
        i=i+1
    dataRanges = (ranges(datainrow))
    return dataRanges

def deleteFolderContents(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
'''
Cycles for each File in the downloads folder, so that it covers each pdf.
Can be changed to be within a loop which downloads the PDFs
To do that, need to replace 'for each file' with 'latest file'
'''
print('Beginning')


output = []

#Variables to calculate time per PDF and page
avgtimeperPDF=0
maxtimeperPDF=0
mintimeperPDF=0
pdfCount = 0
avgtimeperPage=0
maxtimeperPage=0
mintimeperPage=0
pageCount=0

#For each unfiltered PDF
for unfilteredPDFPath in os.listdir(downloadPath):
    pdfStart = time.time()


    print(unfilteredPDFPath)
    filteredPages = [] #list to hold pages with relevant key words
    print(downloadPath+'\\'+unfilteredPDFPath)
    pages = convert_from_path(downloadPath+'\\'+unfilteredPDFPath, 350,poppler_path=poppler_path) #converts a PDF to a list of images
    print(pages)
    #Useful for bug testing, can be commented out
    print('Searching Pages for Data')
    print('Number of pages being searched: ', len(pages))

    imageCount = 0 #cv2 requires an image path, so the image is stored locally using image count as name
    cumulateArray = [] #Stores the extracted Data from the filtered PDF Pages
    
    for page in pages:
        pageStart = time.time()
        imagePath = tempImagePath+'\\page'+str(imageCount)+'.jpg'
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
            
            dataRanges = getDataRangesFromImage(image[:, :, 0])
            '''
            Gets a list of pairs of numbers. 
            each pair represents a set of concurrent rows where data is found
            this used to extract each line data from the image
            '''
            #print('Data Ranges: ')
            #print(dataRanges)

            
            for foundData in dataRanges:
                #print(foundData)
                currentImage = []
                rangeList = list(foundData)

                if rangeList[1] - rangeList[0] > 1: #if there is more than 1 consecutive row with data
                    #print('checking data ranges:')
                    #print(rangeList[0])
                    #print(rangeList[1])
                    #print('image length',len(image[:, :, 0]))
                    #adds buffer to lower bound
                    if rangeList[0] >=2:
                        lowerBound = (rangeList[0])-2
                    else:
                        lowerBound = 0
                    #adds buffer to upper bound
                    if rangeList[1] < (len(image[:, :, 0]))-3:
                        upperBound = (rangeList[1])+3
                        #print('not last 3 element')
                    else:
                        upperBound = len(image[:, :, 0])
                        #print('last 3 element')
                    
                    #print('Lower Bound',lowerBound)
                    #print('Upper Bound',upperBound)
                    
                    #uses bounds to create image of current selection
                    for i in range(lowerBound,upperBound):
                        #print('adding row: ',i)
                        currentImage.append(image[:, :, 0][i])
                    '''
                    Exports current data row as image
                    Need to do this as, the function to create a cv2 image object, needed to use OCR,
                    requires a filepath, rather than passing a variable
                    '''
                    if currentImage:
                        currentImage = np.asarray(currentImage)
                        #print('Current Image Array')
                        #print(currentImage)
                        #im = Image.fromarray(currentImage)
                        #im.save(str(foundData)+"your_file.jpeg")
                        cv2.imwrite(tempImagePath+'/dataRange'+str(foundData)+".jpeg", currentImage)
                        '''
                        TODO Import currentImage into a a temporary, local, folder
                        '''
                        
                        dataRowImage = cv2.imread(tempImagePath+'/dataRange'+str(foundData)+".jpeg")
                        imageArray = np.array(dataRowImage[:, :, 0]).T
                        charRanges = getDataRangesFromImage(imageArray)
                        #print(charRanges)

                        consData = []
                        dataRowRanges = []
                        while charRanges:
                            #print('Begining While Loop')
                            #print('charRanges')
                            #print(charRanges)
                            outputList=[]
                            outputList.append(charRanges[0])
                            maxVal = 0
                            if len(charRanges) > 1:
                                #print('Multiple Tuples Left')
                                for i in range(len(charRanges)):
                                    #print(len(charRanges))
                                    
                                    if (i+1 != len(charRanges)) and (charRanges[i+1][0] - charRanges[i][1] <=10):
                                        #print(charRanges[i+1][0] - charRanges[i][1] <=10)
                                        outputList.append(charRanges[i+1])
                                        maxVal = i+1
                                    else:
                                        break
                            

                            #print('outputList')
                            #print(outputList)
                            consData.append([outputList])
                            charRanges = charRanges[maxVal+1:]
                        #print(consData)

                        for i in consData:
                            #print(i[0][0][0])
                            #print(i[0][-1][1])
                            dataRowRanges.append((i[0][0][0],i[0][-1][1]))

                        #print(dataRowRanges)

                        j=0
                        p = 10
                        textArray = []
                        for i in dataRowRanges:
                            #print(i[0])
                            #print(i[1])

                            currentImage = ((imageArray[i[0]:i[1]].T))
                            currentImage = np.c_[np.full((len(currentImage), p), 255), currentImage, np.full((len(currentImage), p), 255) ]
                            currentImage = np.r_[[currentImage[0]]*p,currentImage,[currentImage[-1]]*p]

                            im = Image.fromarray(currentImage)
                            if im.mode != 'RGB':
                                im = im.convert('RGB')
                            im.save(tempImagePath+'\\DataColumnRanges'+str(j)+".jpeg")
                            imageWord = cv2.imread(tempImagePath+'\\DataColumnRanges'+str(j)+".jpeg")
                            #print('OCR on Image')
                            text = str(pytesseract.image_to_string(imageWord)).rstrip()
                            #print(text)
                            textArray.append(text)
                            j+=1
                        #print(textArray)
        



                        '''
                        Extracts text from the dataRowImage
                        Converts text into an array of each block of words
                        The data we are looking for, will always have the last two words as the numbers, and the rest as the label
                        Therefore, the last two words are extracted into y0, and y1, and the rest are extracted into a label variable
                        These are then appended to a dataframe for the current PDF.
                        This dataframe can then be manipulated to create an csv
                
                        '''
                        #text = str(pytesseract.image_to_string(dataRowImage)).rstrip()
                        #textArray = toList(text.rstrip("\n"))
                        y0=''
                        y1=''
                        label=''
                        if len(textArray) >=3:#TODO make length variable
                            y0 = textArray[-2]
                            y1 = textArray[-1]
                            label = ' '.join(textArray[:-1])
                            outputArray = [label,y0,y1]#TODO make output variable
                            #print(outputArray)
                            cumulateArray.append(outputArray)
                        
                        #print('Cumulate Array')
                        #print(cumulateArray)
        deleteFolderContents(tempImagePath)

        pageTime = time.time() - pageStart

        if (pageCount>0) and (maxtimeperPage<pageTime):
            maxtimeperPage = pageTime
        elif (pageCount>0) and (mintimeperPage>pageTime):
            mintimeperPage = pageTime
        elif pageCount==0:
            maxtimeperPage = pageTime
            mintimeperPage = pageTime
            avgtimeperPage = pageTime
        pageCount+=1
        avgtimeperPage += (pageTime-avgtimeperPage)/pageCount
    '''
    Creates dataframe from extracted data data
    3 columns: label, y0 and y1
    y1 = last word in row
    y0 = second to last word in row
    label = the rest of the row

    regex is used to filter the y0, and y1, columns down to just numbers
    in the format we want
    '''
    #print(cumulateArray)

    df = pd.DataFrame(cumulateArray)
    #print(df)
    if not df.empty:
        df.columns = ['Label','Y0','Y1']
        #print(df)
        df = df.replace('\n','', regex=True)
        df['Y1'] = df['Y1'].replace(r'[^0-9()^.]','', regex=True)
        df['Y0'] = df['Y0'].replace(r'[^0-9()^.]','', regex=True)
        

        df['Y0'] = df['Y0'].replace(['.','(',')','()'],None)
        df['Y1'] = df['Y1'].replace(['.','(',')','()'],None)
        #df = df.dropna(subset=['Y0', 'Y1'], thresh='all')
        #df = df[(df.Y0 != '')or(df.Y1 != '')]
    else:
        df = pd.DataFrame([['' for col in range(3)] for row in range(1)])
        df.columns = ['Label','Y0','Y1']

    print(df)

    #df.to_csv('example.csv',index=False) 
    #df = pd.read_csv(r'example.csv')

    inds = df[["Y0", "Y1"]].isnull().all(axis=1) 
    df = df.loc[~inds, :]
    print(df)
    turnoverY0=''
    turnoverY1=''
    revenueY0='' 
    revenueY1 =''
    costofsalesY0=''
    costofsalesY1=''
    grossprofitY0=''
    grossprofitY1 =''
    distributionexpensesY0=''
    distributionexpensesY1 =''
    profitbeforetaxY0=''
    profitbeforetaxY1=''

    for index, row in df.iterrows():
        outputRow=[]
        if 'revenue' in row['Label'].replace(" ", "").lower():
            revenueY0 = row['Y0']
            revenueY1 = row['Y1']
        elif 'turnover' in row['Label'].replace(" ", "").lower():
            turnoverY0 = row['Y0']
            turnoverY1 = row['Y1']
        elif 'costofsale' in row['Label'].replace(" ", "").lower():
            costofsalesY0 = row['Y0']
            costofsalesY1 = row['Y1']
        elif 'grossprofit' in row['Label'].replace(" ", "").lower():
            grossprofitY0 = row['Y0']
            grossprofitY1  = row['Y1']
        elif 'distributionexpenses' in row['Label'].replace(" ", "").lower():
            distributionexpensesY0 = row['Y0']
            distributionexpensesY1  = row['Y1']
        elif 'profitbeforetax' in row['Label'].replace(" ", "").lower():
            profitbeforetaxY0 = row['Y0']
            profitbeforetaxY1  = row['Y1']
    #df.to_csv('example.csv',index=False) 
    output = [unfilteredPDFPath[:-4],
            revenueY0,
            revenueY1,
            turnoverY0,
            turnoverY1,
            costofsalesY0,
            costofsalesY1,
            grossprofitY0,
            grossprofitY1,
            distributionexpensesY0,
            distributionexpensesY1,
            profitbeforetaxY0,
            profitbeforetaxY1]
    if Path(outputfilePath).is_file():
        print(output)
        with open("output.csv","a", newline="") as fp:
            wr = csv.writer(fp)
            wr.writerow(output)
    else:
        print(output)
        df_output = pd.DataFrame([output], columns=['Number',
                                'revenueY0',
                                'revenueY1',
                                'turnoverY0',
                                'turnoverY1',
                                'costofsalesY0',
                                'costofsalesY1',
                                'grossprofitY0',
                                'grossprofitY1',
                                'distributionexpensesY0',
                                'distributionexpensesY1',
                                'profitbeforetaxY0',
                                'profitbeforetaxY1'])

        df_output.to_csv('Output.csv',index=False)
    pdfTime = time.time() - pdfStart

    if (pdfCount>0) and (maxtimeperPDF<pdfTime):
        maxtimeperPDF = pdfTime
    elif (pdfCount>0) and (mintimeperPDF>pdfTime):
        mintimeperPDF = pdfTime
    elif pdfCount==0:
        maxtimeperPDF = pdfTime
        mintimeperPDF = pdfTime
        avgtimeperPDF = pdfTime
    pdfCount+=1
    avgtimeperPDF += (pdfTime-avgtimeperPDF)/pdfCount

print('Average Time per PDF: ',avgtimeperPDF)
print('Max Time per PDF: ',maxtimeperPDF)
print('Min Time per PDF: ',mintimeperPDF)

print('Average Time per Page: ',avgtimeperPage)
print('Max Time per Page: ',maxtimeperPage)
print('Min Time per Page: ',mintimeperPage)
