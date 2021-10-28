from WebScraping import CompanyNames
import PyPDF2
from PyPDF2 import PdfFileWriter, PdfFileReader
import os

filepath_down = r'F:\WebScraping\CSV test 0.2\Downloads'
filepath_fil = r'F:\WebScraping\CSV test 0.2\Filtered'
CompanyDirs = []

directory_contents = os.listdir(filepath_down)
CompanyNames = [ x for x in directory_contents if ".txt" not in x ]
print(CompanyNames)



errorFiles = []
errors = []
for name in CompanyNames:
    currfilepath = filepath_down+'\\'+name
    print('Beginning '+name+' files')
    try:
        os.mkdir(filepath_fil+'\\'+name)
        #print('Created Directory')
    except FileExistsError:
        print('FOLDER ALREADY EXISTS: '+filepath_fil+'\\'+name)
    try:
        for fname in os.listdir(filepath_down+'\\'+name):
            file = open(filepath_down +'\\'+ name +'\\'+fname,'rb')
            infile = PdfFileReader(file,'rb')
            output = PdfFileWriter()
            
            pages_to_keep = []
            
            try:
                for i in range(infile.numPages):
                    page = infile.getPage(i)
                    text = page.extractText()
                    if any(ext in text for ext in ['co2','CO2e','scope 1','Scope 1']):
                        #print(i)
                        pages_to_keep.append(i)
                
            
                if not pages_to_keep:
                    print('No Keyword Found: '+name+'\\'+fname)
                else:
                    pages_to_keep.insert(0,0)#inserts the first page into the list of pages to keep
                    pages_to_keep = list(set(pages_to_keep))#removes duplicate pages incase first page was already in the list
                    for i in pages_to_keep:
                        p = infile.getPage(i)
                        output.addPage(p)
                    with open(filepath_fil +'\\'+name+'\\'+fname, 'wb') as f:
                        output.write(f)
            except (PyPDF2.utils.PdfReadError,KeyError,PermissionError,ValueError) as e:
                print('Error: ',name+'\\'+fname)
                errorFiles.append(name+'\\'+fname)
                errors.append(e)
    except (PermissionError,PyPDF2.utils.PdfReadError) as e:
        print('Error: ',name+'\\'+fname)
        errorFiles.append(name+'\\'+fname)
        errors.append(e)

with open(filepath_fil+'\Errors.txt', 'w') as f:
    for item in errorFiles:
        f.write("%s\n" % item)
print(errors)
