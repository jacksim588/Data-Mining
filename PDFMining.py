import PyPDF2
from PyPDF2 import PdfFileWriter, PdfFileReader
from tableExtraction import extractTables
import os
import math


def minePDFs(filePath,name):
    errorFiles = []
    errors = []
    filepath_down = filePath+'\\'+name+'\\Unfiltered'
    filepath_fil = filePath+'\\'+name+'\\Filtered'
    print('Filtering PDFs for ',name)
    try:
        os.mkdir(filepath_fil)
    except FileExistsError:
        print('FOLDER ALREADY EXISTS')
    try:
        for fname in os.listdir(filepath_down):
            print('Filtering: ', fname)
            file = open(filepath_down +'\\'+fname,'rb')
            infile = PdfFileReader(file,'rb')
            output = PdfFileWriter()
            
            pages_to_keep = []
            
            try:
                for i in range(infile.numPages):
                    page = infile.getPage(i)
                    text = page.extractText()
                    if any(ext in text for ext in ['scope 1','Scope 1']):
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
                    if len(filepath_fil+'\\'+fname+fname+' table 0')>250:
                        print('Filepath too long: Truncating file name')
                        try:
                            length = int(math.ceil((len(filepath_fil +'\\'+fname+fname+' table 0')-250)/2))
                            print(length)
                            fname = fname[:-4]
                            print(fname[0:-length]+'.pdf')
                            fname = fname[0:-length]+'.pdf'
                        except Exception as e:
                            print('File name too long, Error truncating file: ',e)
                    with open(filepath_fil+'\\'+fname, 'wb') as f:
                        output.write(f)
            except (PyPDF2.utils.PdfReadError,KeyError,PermissionError,ValueError) as e:
                print('Error: ',name+'\\'+fname)
                errorFiles.append(name+'\\'+fname)
                errors.append(e)

            #Extract CSVs
            extractTables()
    except (PermissionError,PyPDF2.utils.PdfReadError) as e:
        print('Error: ',name+'\\'+fname)
        errorFiles.append(name+'\\'+fname)
        errors.append(e)

    with open(filepath_fil+'\Errors.txt', 'w') as f:
        for item in errorFiles:
            f.write("%s\n" % item)
