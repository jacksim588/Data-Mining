import PyPDF2
from PyPDF2 import PdfFileWriter, PdfFileReader
import os

CompanyNames = ['asda','NEXT','greene king','santander','HSBC','Unilever','aviva','Tesco','airbus','vauxhall']
filepath_down = r'F:\Webscraping\Downloads'
filepath_fil = r'F:\Webscraping\Filtered'
for name in CompanyNames:
    currfilepath = filepath_down+'\\'+name

    try:
        os.mkdir(filepath_fil+'\\'+name)
    except FileExistsError:
        print('FOLDER ALREADY EXISTS: '+filepath_fil+'\\'+name)

    for fname in os.listdir(filepath_down+'\\'+name):
        file = open(filepath_down +'\\'+ name +'\\'+fname,'rb')
        infile = PdfFileReader(file,'rb')
        output = PdfFileWriter()

            
        pages_to_keep = []
        for i in range(infile.numPages):
            page = infile.getPage(i)
            text = page.extractText()
            if any(ext in text for ext in ['CO2e']):
                print(i)
                pages_to_keep.append(i)
        for i in pages_to_keep:
            p = infile.getPage(i)
            output.addPage(p)
        if not pages_to_keep:
            print('No Keyword Found: '+name+'\\'+fname)
        else:
            with open(filepath_fil +'\\'+name+'\\'+fname, 'wb') as f:
                output.write(f)