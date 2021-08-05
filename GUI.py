from os import name
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter.font import Font
import tkinter.font as font
import WebScraping
import csv
import os

'''
NOTES FOR IMROVEMENT

-This site cant be reached errors:
SAFEWAY STORES LIMITED

-It looks like there aren't many great matches for your search:
SAFEWAY STORES LIMITED

'''
#Roboto

master = Tk()
master.geometry("500x200")
master.title('Company Data Bot')
master['bg'] = '#fcfaea'


text = tk.Text(master)
myFont = font.Font(family='Roboto')
text.configure(font=myFont)

master.columnconfigure(0, weight=1)
master.columnconfigure(1, weight=2)



Label(master, text='Company Name File',bg='#fcfaea',fg='#262626',font=myFont).grid(row=0)
Label(master, text='',bg='#fcfaea',fg='#262626',font=myFont).grid(row=1,column=4)
Label(master, text='Criteria Text',bg='#fcfaea',fg='#262626',font=myFont).grid(row=2)
Label(master, text='',bg='#fcfaea',fg='#262626',font=myFont).grid(row=3)
Label(master, text='Download Folder',bg='#fcfaea',fg='#262626',font=myFont).grid(row=4)


folder_path = StringVar()


def browse_button_companyNameDir():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global folder_path
    filename = filedialog.askopenfile()
    print(filename.name)
    folder_path.set(filename)
    e_companyNameDir.insert(0,filename.name)

def browse_button_DownloadDir():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global folder_path
    filename = filedialog.askdirectory()
    filename = os.path.normpath(filename) 
    print(filename)
    folder_path.set(filename)
    e_DownloadDir.insert(0,filename)

def onPress():
    print('Button Pressed')
    namePath = e_companyNameDir.get()
    namePath.encode('unicode_escape')
    print(namePath)
    with open(namePath,'r', encoding='utf-8-sig') as csv_file:
        copmanies = csv_file.read().splitlines() 
    print(copmanies)
    WebScraping.WebScraper(
        copmanies,
        e_criteria.get(),
        e_DownloadDir.get()
    )


e_companyNameDir = Entry(master,font=myFont)
e_criteria = Entry(master,font=myFont)
e_DownloadDir = Entry(master,font=myFont)
e_companyNameDir.grid(row=0, column=1)
e_criteria.grid(row=2, column=1)
e_DownloadDir.grid(row=4, column=1)

browseButtonNames = tk.Button(master, text='Select File', command=browse_button_companyNameDir,bg='#faf4ef',fg='#262626',font=myFont)
browseButtonDownload = tk.Button(master, text='Select Folder', command=browse_button_DownloadDir,bg='#faf4ef',fg='#262626',font=myFont)
submitButton = tk.Button(master, text='Start Bot', command=onPress,bg='#faf4ef',fg='#262626',font=myFont)
submitButton.grid(row=5, column=1)
browseButtonNames.grid(row=0,column=3)
browseButtonDownload.grid(row=4, column=3)
mainloop()