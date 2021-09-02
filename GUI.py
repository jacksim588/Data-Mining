from os import name
import tkinter as tk
import tkcalendar
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.font import Font
from tkcalendar import DateEntry
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

-Network Errors:
APPLE EUROPE LIMITED

-Could Add an Output File with failed companies

'''
#Roboto

master = Tk()
master.geometry("500x200")
master.title('Company Data Bot')
master['bg'] = '#fcfaea'


style = ttk.Style()

style.theme_create( "mainStyle", parent="alt", settings={
        "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
        "TNotebook.Tab": {
            "configure": {"padding": [5, 1], "background": '#fcfaea' },
            "map":       {"background": [("selected", '#fcfaea')],
                          "expand": [("selected", [1, 1, 1, 0])] } } } )
                   
style.theme_use("mainStyle")
tabControl = ttk.Notebook(master,style='TNotebook')
tab_main = ttk.Frame(tabControl)
tab_settings = ttk.Frame(tabControl)
tabControl.add(tab_main, text='Main')
tabControl.add(tab_settings, text='Settings')
tabControl.pack(fill=BOTH, expand=True)
tabControl



text = tk.Text(master)
myFont = font.Font(family='Roboto')
text.configure(font=myFont)

tab_main.columnconfigure(0, weight=1)
tab_main.columnconfigure(1, weight=2)



Label(tab_main, text='Company Name File',bg='#fcfaea',fg='#262626',font=myFont).grid(row=0)
Label(tab_main, text='',bg='#fcfaea',fg='#262626',font=myFont).grid(row=1,column=4)
Label(tab_main, text='Criteria Text',bg='#fcfaea',fg='#262626',font=myFont).grid(row=2)
Label(tab_main, text='',bg='#fcfaea',fg='#262626',font=myFont).grid(row=3)
Label(tab_main, text='Download Folder',bg='#fcfaea',fg='#262626',font=myFont).grid(row=4)
Label(tab_main, text='Date',bg='#fcfaea',fg='#262626',font=myFont).grid(row=5)



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
    if beforeDateVar.get() == 1:
        B_Date = beforeDate.get_date()
    else:
        B_Date = ''
    print(B_Date)

    namePath = e_companyNameDir.get()
    namePath.encode('unicode_escape')
    print(namePath)
    with open(namePath,'r', encoding='utf-8-sig') as csv_file:
        companies = csv_file.read().splitlines() 
    print(companies)
    
    
    
    WebScraping.WebScraper(
        companies,
        e_criteria.get(),
        e_DownloadDir.get(),
        B_Date
    )




e_companyNameDir = Entry(tab_main,font=myFont)
e_criteria = Entry(tab_main,font=myFont)
e_DownloadDir = Entry(tab_main,font=myFont)
e_companyNameDir.grid(row=0, column=1)
e_criteria.grid(row=2, column=1)
e_DownloadDir.grid(row=4, column=1)






beforeDate = DateEntry(tab_settings, width=12, background='darkblue',foreground='white', borderwidth=2, year=2020)
beforeDate.pack(pady=10)
beforeDateVar=IntVar()
beforeDateCheck = Checkbutton(tab_settings, text = "Use Before Date", variable=beforeDateVar)
beforeDateCheck.pack()


browseButtonNames = tk.Button(tab_main, text='Select File', command=browse_button_companyNameDir,bg='#faf4ef',fg='#262626',font=myFont)
browseButtonDownload = tk.Button(tab_main, text='Select Folder', command=browse_button_DownloadDir,bg='#faf4ef',fg='#262626',font=myFont)
submitButton = tk.Button(tab_main, text='Start Bot', command=onPress,bg='#faf4ef',fg='#262626',font=myFont)
submitButton.grid(row=6, column=1)
browseButtonNames.grid(row=0,column=3)
browseButtonDownload.grid(row=4, column=3)
mainloop()