#!/usr/bin/python3
##
## JS8msg is a copyrighted program written by Thomas Kocourek, N4FWD
## This program is released under the GPL v3 license
## 
import tkinter as tk
from tkinter import *
from tkinter import ttk
import sys
from tkinter import messagebox as mb
import globalVariables as gv
#import utilities as ut
import classTab1 as T1
import classTab2 as T2
import classTab3 as T3
import js8setup as js

## Global variables
## All supported forms need to be init'd here
## Otherwise you run into 'scope of variable' problems
ics213FormData = gv.ics213FieldsData 
commonConfData =gv.commonConfData
whichFormUsedExt = gv.whichForm
readDataFlag = gv.readDataFlag
readConfFlag = gv.readConfFlag
respIcs213FormData = gv.respIcs213FormData
notebookTabs = []
formDataToSend = ""
callsignSelected = ""

## added global paths for config file and storing/loading data files
## globalVariables.py

# Root class to create the interface and define the controller function to switch frames
class RootApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(NoteBook)
 
# controller function
    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.grid()
 
# sub-root to contain the Notebook frame and a controller function 
# to switch the tabs within the notebook
class NoteBook(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.notebook = ttk.Notebook(width=800, height=600)
        ## build the list of tabs within the notebook
        ## Each sub-section is a module referenced by "import"
        notebookTabs.append(self.notebook)
        self.tab1 = T1.Tab1(self.notebook)
        notebookTabs.append(self.tab1)
        self.tab2 = T2.Tab2(self.notebook)
        notebookTabs.append(self.tab2)
        self.tab3 = T3.Tab3(self.notebook)
        notebookTabs.append(self.tab3)
        self.tab4 = Tab4(self.notebook)
        notebookTabs.append(self.tab4)
        self.tab5 = Tab5(self.notebook)
        notebookTabs.append(self.tab5)
        ## Note: each Tab will be a different supported form
        ## Add the text of the tab
        self.notebook.add(self.tab1, text="JS8msg Communication")
        self.notebook.add(self.tab2, text="Config")
        self.notebook.add(self.tab3, text="ICS-213")
        self.notebook.add(self.tab4, text="Available")
        self.notebook.add(self.tab5, text="Available")
        self.notebook.grid(row=1)
 
# controller function
    def switch_tab1(self, frame_class):
        new_frame = frame_class(self.notebook)
        self.tab1.destroy()
        self.tab1 = new_frame

### Each tab will be a program function: either configuration or forms

#### ======================== Available Tab ===============================================
class Tab4(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        topRow =0
        ## Quit program button
        quitButton = Button(self, text="Quit", command=lambda:self.quitProgram())
        quitButton.configure(bg="blue", fg="white")
        quitButton.grid(column=1,row=topRow, sticky = "e", padx=20)

    def quitProgram(self):
        sys.exit()
#### ======================== End of Tab ==============================================
##
#### ======================== Available Tab ===============================================
class Tab5(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        topRow =0
        ## Quit program button
        quitButton = Button(self, text="Quit", command=lambda:self.quitProgram())
        quitButton.configure(bg="blue", fg="white")
        quitButton.grid(column=1,row=topRow, sticky = "e", padx=20)

    def quitProgram(self):
        sys.exit()
#### ======================== End of Tab ==============================================
##
## ==================================== End of supported items ========================

if __name__ == "__main__":
    js.setup()
    Root = RootApp()
    Root.geometry("800x600")
    Root.title("JS8msg")
    Root.mainloop()