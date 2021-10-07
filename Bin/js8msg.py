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
import webbrowser as wb
import globalVariables as gv
import utilities as ut
import js8API as api
import os

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
        notebookTabs.append(self.notebook)
        self.tab1 = Tab1(self.notebook)
        notebookTabs.append(self.tab1)
        self.tab2 = Tab2(self.notebook)
        notebookTabs.append(self.tab2)
        self.tab3 = Tab3(self.notebook)
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
#### ======================== JS8msg Control =============================
class Tab1(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        ## Specify column width for form
        colWidth =28

        ## Some Variables for Tab1
        self.dropdown = StringVar()
        self.group = StringVar()
        self.callsignSelected = ""
        self.callsignSelIndex = 0
        self.formDataToSend = "Load a completed form to send."
        self.labelText = "No Call"
        self.labelText2 = "No Message"
        self.groupList = ['@ALLCALL']
        self.callsignList = []
        self.messageList = []
        self.msgListIndex = 0
        self.msgSelected = {}
        self.htmlFile = ""
        self.stationCallSign = ""


        ## build up the callsign list
        def buildCall():
            ## fetch the station callsign from JS8call
            try:
                ## if JS8call is running, the station callsign is returned
                self.stationCallSign = stationCallsign = api.getStationCallsign()
            except:
                mb.showinfo("Error!","Either JS8call is not running or TCP server in JS8call is not running.")
            self.callsignList = []
            ## if we added a group to JS8msg, let's add it to the list
            for x in self.groupList:
                self.callsignList.append(x)
            ## After adding the groups, now add the station callsign
            self.callsignList.append(stationCallsign)
            ## fetch the active callsigns from JS8call
            callList = api.getCallsigns()
            ## Add the active callsigns to the list
            if callList is not None:
                for x in callList:
                ## Only add valid callsigns
                ## Occasionally, the first callsign from JS8call is blank
                    if x:
                        self.callsignList.append(x)
            else:
                mb.showinfo("Error!","Either JS8call is not running or TCP server in JS8call is not running.")
                callList = []
            ## clear out any old list being displayed
            self.chooseList.delete(0,'end')
            ## Add the list of callsigns / groups to the callsign Listbox widget
            index=0
            for x in self.callsignList:
                self.chooseList.insert(index,x)
                index += 1

        def buildMsgList():
            ## self.messageList is a list of dictionaries
            ## Clear any existing message being displayed
            self.chooseMessage.delete(0,"end")
            ## Add the list of groups/callsigns to the messages Listbox widget
            index = 0
            for x in self.messageList:
                self.chooseMessage.insert(index,x["fm"]+', '+x["id"])
                index += 1

        def getGroup():
            ## read the group entered in the group Entry widget
            result=self.group.get().upper()
            if result != "":
                self.groupList.append(self.group.get().upper())
                buildCall()
                ## clear the displayed group from the Entry widget
                self.group.set("")

        ## Callbacks for Combobox()
        def selectMsgOption(event):
            selAction = self.chooseAction.get()
            if selAction == "Load Form":
                loadSourceData()
                self.chooseAction.set('')
            elif selAction == "Send Tx Message":
                sendTxMessage()
                self.chooseAction.set('')
            elif selAction == "Store Message to Inbox":
                storeMessage()
                self.chooseAction.set('')
            elif selAction == "Get messages from Inbox":
                getMessages()
                self.chooseAction.set('')

        ## Callback for ListBox Button
        def retrieve():

            ## self.chooseList.curselection() returns a tuple
            ## select the first element and assign to 'index'
            index = self.chooseList.curselection()
            if index != ():
                select = index[0]
                self.callsignSelected = self.callsignList[select]
                self.callsignSelIndex = select
                self.labelText = "Selected: "+self.callsignSelected
            else:
                ## if someone clicks on the button without selecting
                ## Default to the first element = @ALLCALL
                self.callsignSelected = self.callsignList[0]
                self.callsignSelIndex = 0
                self.labelText = "Selected: "+self.callsignList[0]

            ## Display the selected callsign
            listBoxLabel = Label(self)
            listBoxLabel.grid(column=0,row=1, sticky="sw", padx=13)
            listBoxLabel.configure(text=self.labelText, bg="#d8b8d8", pady=6, width = 23)

        def msgDisplay():
            formDataDict = {}
            textKey = ""
            index=self.chooseMessage.curselection()
            if index != ():
                select = index[0]
                
                ## transfer dictionary from list of dictionaries
                self.msgSelected = self.messageList[select]
                self.labelText2 = self.msgSelected["fm"]+', '+self.msgSelected["id"]

                ## the message could be wrapped and encoded
                if self.msgSelected["mg"][:8] == 'EMCOMMG=':

                    ## pull out message from dictionary. Unwrap and decode it
                    formDecoded = ut.decodeMessage(ut.unwrapMsg(self.msgSelected["mg"]))

                    ## the decoded message will be a string dictionary
                    ## and it has a bunch of extraneous characters which
                    ## need to be stripped out
                    ##
                    ## remove extra quotes from the string
                    formD2List = formDecoded[1:-1].replace('\"','')
                    ## remove \' from the string
                    formDList = formD2List.replace("\\'","'")
                    ## break up the long string into a list
                    formListing = formDList.split(', ')
                    ## walk through the list and build the data dictionary
                    for x in formListing:
                        ## split the string into key and data
                        xList = x.split(': ')
                        ## look for multiline text
                        if xList[0] == "mg":
                            textKey = "mg"
                        elif xList[0] == "rp":
                            textKey = "rp"
                        try:
                            key = xList[0]
                            data = xList[1]
                            ## add a proper key:data pair to the dictionary
                            formDataDict[key] = data
                        except IndexError:
                            ## found multiline text, concatenate lines
                            if len(x[0]) > 0:
                                formDataDict[textKey] = formDataDict[textKey]+'\n'+xList[0]
                    
                    formData = formDataDict

                    ## save data in case a reply is needed
                    ## create a unique file name to save the dictionary
                    ## Use the extension which is part of the data dictionary
                    saveFile = self.stationCallSign+self.msgSelected["id"]+'_recvd.'+formData["file"]
                    ## complete the path
                    saveFilePath = os.path.join(gv.msgPath,saveFile)
                    fh = open(saveFilePath, "w")
                    ## write each line out based on the key
                    for key in gv.totalIcs213Keys:
                        fh.write(key+':'+formData[key]+'\n')
                    fh.close()

                    ## formdata is dictionary
                    formKeys = gv.totalIcs213Keys
                    templateFile = ""
                    if formData["file"] == "213":
                        templateFile = gv.templatePath+"ics213_template.html"
                    ## add 'elif' to use a HTML template for other forms

                    ## outputHtml gives back a HTML document
                    ## parse off the 'file' key from the formKeys, not needed!
                    result = ut.outputHtml(formData, formKeys[:-1], templateFile)

                    ## write the form to a file for the web browser
                    self.htmlFile = gv.tempPath+"temp.html"
                    fh = open(self.htmlFile,"w")
                    for x in result:
                        fh.writelines(x)
                    fh.close()

                    ## clear out text box
                    self.messageTextBox.delete(1.0,END)
                    ## build the URL for the web browser
                    url = 'file://'+os.path.realpath(self.htmlFile)
                    ## open the HTML file in a web browser
                    wb.open(url)
                    ## Sometimes the web browser will send extra messages to the
                    ## Python console
                    ## Clear the Python console of messages from web browser
                    x =1
                    while x < 3:
                        ## wait 1 second and then clear
                        ut.clearConsole()
                        x += 1

                else:
                    ## display regular text in Text box
                    formData = self.msgSelected["mg"]
                    self.messageTextBox.delete(1.0,END)
                    self.messageTextBox.insert(END,formData+'\n')
                ## update the display and show the selected message id
                listBoxLabel2 = Label(self)
                listBoxLabel2.grid(column=0,row=1, sticky="se", padx=13)
                listBoxLabel2.configure(text=self.labelText2, bg="#d8b8d8", pady=6, width = 23)
        
        #### main display of widgets ####
        topRow =0
        ## Add a label and combobox to the display
        self.label = Label(self, text="Select =-> ")
        self.label.grid(column=0,row=topRow, sticky="w")
        self.chooseAction = ttk.Combobox(self, width=colWidth, textvariable = self.dropdown, background="#f8d8d8")
        self.chooseAction['values'] = ["Load Form","Send Tx Message","Store Message to Inbox","Get messages from Inbox"]
        self.chooseAction.grid(column=0,row=topRow, sticky="w", padx=80)
        ## Note: callback function must preceed the combobox widget
        self.chooseAction.bind('<<ComboboxSelected>>', selectMsgOption)

        ## Add a group widgets
        self.groupLabel = Button(self, text="Add Group and Click =-> ", command=getGroup)
        self.groupLabel.grid(column=0, row=topRow, sticky="e", padx=120)
        self.groupEntry = Entry(self, textvariable=self.group, width=14, bg="green1")
        self.groupEntry.grid(column=0, row=topRow, sticky="e")


        ## Quit program button
        quitButton = Button(self, text="Quit", command=lambda:self.quitProgram())
        quitButton.configure(bg="blue", fg="white")
        quitButton.grid(column=1,row=topRow, sticky = "e", padx=20)

        ## set the height of the scrollbars
        vertPad = 32

        ## Next few widgets need to be populated from live JS8call
        listRow = 1
        selRow = 2

        ## Added an Update button for callsigns Listbox
        self.updateButton = Button(self, text = "Update Callsigns", command=buildCall)
        self.updateButton.grid(column=0, row=listRow, sticky="nw")
        self.updateButton.configure(bg="yellow1", width=22)

        ## Add a button to select a callsign from the Listbox for transmitting or the JS8call inbox
        self.listBoxButton = Button(self, text = "Select Callsign & Click here", command=retrieve)
        self.listBoxButton.configure(bg="yellow1", width=22)
        self.listBoxButton.grid(column=0, row=selRow, sticky="w")

        ## Add the callsign Listbox widget
        self.chooseList = Listbox(self, selectmode=SINGLE, selectbackground="#f8f8d8", bg="green1", width=10)
        buildCall()
        self.chooseList.grid(column=0,row = listRow, padx = 13, pady=vertPad, sticky="nw")
        self.chooseList.activate(self.callsignSelIndex)
        self.chooseList.see(self.callsignSelIndex)
        ## add a scrollbar widget for when the callsign list size exceeds the displayed area
        self.scrollBar = Scrollbar(self, orient=VERTICAL, command=self.chooseList.yview)
        self.scrollBar.grid(column=0, row= listRow, pady=vertPad, sticky="nsw")
        ## Link the scrollbar widget to the Listbox widget
        self.chooseList['yscrollcommand'] = self.scrollBar.set


        ## Added button for selecting from the message list 
        self.listMsgButton = Button(self, text = "Select Message & Click here", command=msgDisplay)
        self.listMsgButton.configure(bg="green1", width=22)
        self.listMsgButton.grid(column=0, row=selRow, sticky="se")
        ## Added the messages Listbox widget
        self.chooseMessage = Listbox(self, selectmode=SINGLE, selectbackground="#f8f8d8",bg="green1", width=24)
        buildMsgList()
        self.chooseMessage.grid(column=0, row=listRow, padx=0, pady=vertPad, sticky="ne")
        self.chooseMessage.activate(self.msgListIndex)
        self.chooseMessage.see(self.msgListIndex)
        ## Added a scrollbar widget for when the messages list size exceeds the displayed area
        self.msgScrollBar = Scrollbar(self, orient=VERTICAL, command=self.chooseMessage.yview)
        self.msgScrollBar.grid(column=0, row=listRow, pady=vertPad, sticky="nse", padx=196)
        ## Link the scrollbar widget to the Listbox widget
        self.chooseMessage['yscrollcommand'] = self.msgScrollBar.set


        txtRow = 3
        ## Added a general purpose Text area to the display
        self.messageTextBox = Text(self)
        self.messageTextBox.grid(column=0, row=txtRow, sticky="w")
        self.messageTextBox.configure(background="#f8d8d8", wrap="word")
        self.messageTextBox.delete(1.0,END)
        self.messageTextBox.insert(END,self.formDataToSend)

#### Form messages will be 'wrapped' so as to destinguish between normal text
#### and a form which will need displaying in the web browser
        def sendTxMessage():
            ## valid if you selected a destination callsign
            if self.callsignSelected:
                ## use the contents of the Text area
                ## which is stored in self.formDataToSend
                ## send it to JS8call for transmitting immediately
                ## self.formDataToSend is encoded and wrapped in 'api.sendLive'
                result = api.sendLive(self.callsignSelected,self.formDataToSend)
                if result is None:
                    mb.showwarning(None,"Problem with JS8call transmitting message.")
            else:
                ## remind them to select a destination callsign
                mb.showinfo("No callsign selected","Select one from the list of callsigns.")         

        def storeMessage():
            ## valid if you selected a destination callsign
            if self.callsignSelected:
                ## self.formDataToSend is encoded and wrapped in 'api.sendToInbox'
                result = api.sendToInbox(self.callsignSelected,self.formDataToSend)
                if result is not None:
                    mb.showinfo("Result","Message is stored in Inbox!")
                else:
                    mb.showwarning(None,"Problem with JS8call storing message.")
            else:
                mb.showinfo("No callsign selected","Select one from the list of callsigns.")

        def getMessages():
            ## getInbox returns a list of dictionaries from JS8call
            result = api.getInbox()
            if result:
                ## self.messageList will hold a list of dictionaries
                ## each dictionary will hold callsign, message text, and messageID
                ## if wrapped, the message remains the same
                ## display needs the wrap to differenciate between forms and text
                self.messageList = result
                self.chooseMessage.delete(0,END)
                index = 0
                for x in self.messageList:
                    self.chooseMessage.insert(index,x["fm"]+', '+x["id"])
                    index += 1
            else:
                mb.showwarning(None,"Problem fetching messages from inbox")



        def loadSourceData():
            fileData = [("ICS-213 Forms","*.213")]
            funcParam = (gv.msgPath,fileData)
            ## returns a dictionary
            result = ut.loadFormData(funcParam)
            ## convert from a dictionary to a string 
            formDataToSend = ut.dictToString(result)
            ## update Text box
            self.messageTextBox.delete(1.0,END)
            self.messageTextBox.insert(END,formDataToSend+'\n')
            self.formDataToSend = formDataToSend 

          

    def quitProgram(self):
        ## check if the temporary HTML file exists
        if self.htmlFile:
            ## delete it
            os.remove(self.htmlFile)
        sys.exit()
#### ======================== End of JS8msg Control ===============================
##
#### ======================== Start of Configuration ===================================
##
## Common Configuration Data
class Tab2(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        # Keep track of widgets added to frame
        self.widgets = []

        ## More variables
        self.commonConfText = gv.commonConfText
        self.commonConfKeys = gv.commonConfKeys
        self.commonConfData = gv.commonConfData

        ## textvariable for combobox()
        self.dropdown = StringVar()

        ## textvariables for the configuration data entries   
        self.callsignEntryData = StringVar()
        self.phoneEntryData = StringVar()
        self.nameEntryData = StringVar()
        self.addressEntryData = StringVar()
        self.cityEntryData = StringVar()
        self.emailEntryData = StringVar()
        self.formatDateEntryData = StringVar()
        self.formatTimeEntryData = StringVar()
        self.fileEntryData = StringVar()

        # callback function for combobox()
        def selectAction(event):
            selAction = self.chooseConfig.get()
            saveConfData()
            if selAction == "Personal":
                ut.clearWidgetForm(self.widgets)
                personalConf()
                self.chooseConfig.set('')
            elif selAction == "Date/Time":
                ut.clearWidgetForm(self.widgets)
                datetime()
                self.chooseConfig.set('')
            elif selAction == "Radiogram":
                ut.clearWidgetForm(self.widgets)
                radiogramItems()
                self.chooseConfig.set('')
            elif selAction == "Save Configuration to file":
                ut.clearWidgetForm(self.widgets)
                saveData()
                self.chooseConfig.set('')
            elif selAction == "Load Configuration from file":
                ut.clearWidgetForm(self.widgets)
                loadData()
                self.chooseConfig.set('')
            elif selAction == "Clear Configuration":
                ut.clearWidgetForm(self.widgets)
                clearData()
                self.chooseConfig.set('')

        ## Specify column width for form
        colWidth =28
        ## Keep track of which configuration area is being filled in
        self.tableArea = ""

        self.label = Label(self, text="Select =-> ")
        self.label.grid(column=0,row=0, sticky="w")
        self.chooseConfig = ttk.Combobox(self, width=colWidth, textvariable = self.dropdown)
        self.chooseConfig['values'] = ["Personal","Date/Time","Radiogram","Save Configuration to file","Load Configuration from file","Clear Configuration"]
        self.chooseConfig.grid(column=0,row=0, sticky="w",padx=80)
        ## Note callback function must preceed the combobox widget
        self.chooseConfig.bind('<<ComboboxSelected>>', selectAction)

        self.blankLabel = Label(self)
        self.blankLabel.config(text = '     ')
        self.blankLabel.grid(column=2,row=0, sticky="w")

        quitButton = Button(self, text="Quit", command=lambda:self.quitProgram())
        quitButton.grid(column=4,row=0, sticky = "e")
        quitButton.configure(bg="blue", fg="white")

        def personalConf():
            ## Table Entry Area
            self.tableArea = "personal"

            ## widget list keeps track of the displayed widgets
            ## and is used to clear the screen of widgets before
            ## displaying a new set of widgets
            ## reset widget list
            self.widgets = []

            ## Callsign
            callsignRow = 1
            personalCallsignLabel = Label(self,text=self.commonConfText["call"])
            self.widgets.append(personalCallsignLabel)
            personalCallsignLabel.grid(column=0, row= callsignRow, sticky ="w")

            personalCallsignEntry = Entry(self, textvariable = self.callsignEntryData, width=colWidth)
            self.widgets.append(personalCallsignEntry)
            personalCallsignEntry.grid(column=1, row=callsignRow,  columnspan=2, sticky="w")
            ## first clear any text
            personalCallsignEntry.delete(0,END)
            ## Insert any new text
            personalCallsignEntry.insert(0,self.commonConfData["call"])

            ## Name
            nameRow = 2
            personalNameLabel = Label(self,text=self.commonConfText["name"])
            self.widgets.append(personalNameLabel)
            personalNameLabel.grid(column=0, row= nameRow, sticky ="w")

            personalNameEntry = Entry(self, textvariable = self.nameEntryData, width=colWidth)
            self.widgets.append(personalNameEntry)
            personalNameEntry.grid(column=1, row=nameRow,  columnspan=2, sticky="w")
            ## first clear any text
            personalNameEntry.delete(0,END)
            ## Insert any new text
            personalNameEntry.insert(0,self.commonConfData["name"])

            ## Telephone #
            phoneRow = 3
            personalPhoneLabel = Label(self,text=self.commonConfText["phone"])
            self.widgets.append(personalPhoneLabel)
            personalPhoneLabel.grid(column=0, row = phoneRow, sticky="w")

            personalPhoneEntry = Entry(self, textvariable= self.phoneEntryData, width=colWidth)
            self.widgets.append(personalPhoneEntry)
            personalPhoneEntry.grid(column=1, row=phoneRow, columnspan=2, sticky="w")
            ## first clear any text
            personalPhoneEntry.delete(0,END)
            ## Insert any new text
            personalPhoneEntry.insert(0,self.commonConfData["phone"])

            ## Address
            addrRow = 4
            personalAddressLabel= Label(self, text=self.commonConfText["addr"])
            self.widgets.append(personalAddressLabel)
            personalAddressLabel.grid(column=0, row=addrRow, sticky="w")

            personalAddressEntry = Entry(self, textvariable= self.addressEntryData, width=colWidth)
            self.widgets.append(personalAddressEntry)
            personalAddressEntry.grid(column=1, row=addrRow, columnspan=2, sticky="w")
            ## first clear any text
            personalAddressEntry.delete(0,END)
            ## Insert any new text
            personalAddressEntry.insert(0,self.commonConfData["addr"])

            ## City/State/Zip
            cszRow = 5
            personalCszLabel= Label(self, text=self.commonConfText["c-s-z"])
            self.widgets.append(personalCszLabel)
            personalCszLabel.grid(column=0, row=cszRow, sticky="w")

            personalCszEntry = Entry(self, textvariable= self.cityEntryData, width=colWidth)
            self.widgets.append(personalCszEntry)
            personalCszEntry.grid(column=1, row=cszRow, columnspan=2, sticky="w")
            ## first clear any text
            personalCszEntry.delete(0,END)
            ## Insert any new text
            personalCszEntry.insert(0,self.commonConfData["c-s-z"])

            ## Email Address
            emailRow = 6
            personalEmailLabel = Label(self, text=self.commonConfText["email"])
            self.widgets.append(personalEmailLabel)
            personalEmailLabel.grid(column=0, row=emailRow, sticky="w")

            personalEmailEntry = Entry(self, textvariable= self.emailEntryData, width=colWidth)
            self.widgets.append(personalEmailEntry)
            personalEmailEntry.grid(column=1, row=emailRow, columnspan=2, sticky="w")
            ## first clear any text
            personalEmailEntry.delete(0,END)
            ## Insert any new text
            personalEmailEntry.insert(0,self.commonConfData["email"])

        def datetime():
            ## Table Entry Area
            self.tableArea = "datetime"
            ## reset widget list
            self.widgets = []
            
            dtRow = 1
            datetimeDateLabel = Label(self,text=self.commonConfText["fdate"])
            self.widgets.append(datetimeDateLabel)
            datetimeDateLabel.grid(column=0, row= dtRow, sticky ="w")

            dateFormatText = [("YYYY-MM-DD","1"),("YYYY-DD-MM","2"),("MM/DD/YY","3"),("DD/MM/YY","4"),("YYYYMMDD","5")]
            timeFormatText = [("hhmmL","1"),("hh:mmL","2"),("hhmmZ","3"),("hh:mmZ","4"),("hhmm UTC","5"),("hh:mm UTC","6")]

            ## Set up first radiobutton list for date formats
            radioRow = dtRow
            #indexCount = 0
            for format in dateFormatText:
                dateFormat = ttk.Radiobutton(self, text = format[0], value = format[1], variable = self.formatDateEntryData)
                self.widgets.append(dateFormat)
                dateFormat.grid(column=1, row=radioRow, sticky="w")
                radioRow += 1
            self.formatDateEntryData.set(commonConfData["fdate"])

            datetimeTimeLabel = Label(self,text=self.commonConfText["ftime"])
            self.widgets.append(datetimeTimeLabel)
            datetimeTimeLabel.grid(column=2, row=dtRow, sticky="w")

            ## Set up second radiobutton list for time formats
            radioRow = dtRow
            for format in timeFormatText:
                timeFormat = ttk.Radiobutton(self, text = format[0], value = format[1], variable = self.formatTimeEntryData)
                self.widgets.append(timeFormat)
                timeFormat.grid(column=3, row=radioRow, sticky ="w")
                radioRow += 1
            self.formatTimeEntryData.set(commonConfData["ftime"])

        def radiogramItems():
            ## reset widget list
            self.widgets = []
            print("Misc. Items of Form")
            pass
        
        def loadData():
            os.chdir(gv.configPath)
            self.widgets=[]
            fileNameList = [("JS8msg.cfg","*.cfg")]
            funcParam = (gv.configPath,fileNameList)
            result = ut.loadFormData(funcParam)
            if result is not None:
                self.commonConfData = commonConfData = result
                mb.showinfo("Load","Configuration data was loaded")
            else:
                mb.showinfo("Load","ERROR! Configuration data was not loaded")

        def saveData():
            self.widgets=[]
            ## save config in current directory
            fileNameList = [("JS8msg.cfg","*.cfg")]
            funcParam = (gv.configPath,fileNameList,commonConfData,self.commonConfKeys)
            result = ut.saveFormData(funcParam)
            if result is not None:
                mb.showinfo("Save","Configuration data was saved")
            else:
                mb.showinfo("Save","ERROR! Configuration data was not saved")

        def clearData():
            self.widgets=[]
            dtRow = 1
            clearDataLabel = Label(self,text="Clearing configuration data.")
            self.widgets.append(clearDataLabel)
            clearDataLabel.grid(column=0, row= dtRow, sticky ="w")
            for key in self.commonConfKeys:
                if key == "call":
                    commonConfData[key] = ""
                    self.callsignEntryData.set("")
                elif key == "phone":
                    commonConfData[key] = ""
                    self.phoneEntryData.set("")
                elif key == "name":
                    commonConfData[key] = ""
                    self.nameEntryData.set("")
                elif key == "addr":
                    commonConfData[key] = ""
                    self.addressEntryData.set("")
                elif key == "c-s-z":
                    commonConfData[key] = ""
                    self.cityEntryData.set("")
                elif key == "email":
                    commonConfData[key] = ""
                    self.emailEntryData.set("")
                elif key == "fdate":
                    commonConfData[key] = ""
                    self.formatDateEntryData.set("")
                elif key == "ftime":
                    commonConfData[key] = ""
                    self.formatTimeEntryData.set("")
                elif key == "fUTC":
                    commonConfData[key] = ""
            clearDataLabel['text'] = "Configuration data cleared."



        def saveConfData():
            if self.tableArea == "personal":
                for key in self.commonConfKeys:
                    ## Transfer user input from StringVar to data dictionary
                    if key == "call":
                        commonConfData[key] = self.callsignEntryData.get()
                    elif key == "phone":
                        commonConfData[key] = self.phoneEntryData.get()
                    elif key == "name":
                        commonConfData[key] = self.nameEntryData.get()
                    elif key == "addr":
                        commonConfData[key] = self.addressEntryData.get()
                    elif key == "c-s-z":
                        commonConfData[key] = self.cityEntryData.get()
                    elif key == "email":
                        commonConfData[key] = self.emailEntryData.get()
            elif self.tableArea == "datetime":
                for key in self.commonConfKeys:
                    if key == "fdate":
                        commonConfData[key] = self.formatDateEntryData.get()
                    elif key == "ftime":
                        commonConfData[key] = self.formatTimeEntryData.get()
                    elif key == "fUTC":
                        ## Which time format did they select
                        timeValue = self.formatTimeEntryData.get()
                        ## set fUTC to a value determined by the time format
                        if timeValue == "1" or timeValue == "2":
                            commonConfData[key] = "0"
                        elif timeValue == "3" or timeValue == "4":
                            commonConfData[key] = "1"
                        elif timeValue == "5" or timeValue == "6":
                            commonConfData[key] = "2"


                
    def quitProgram(self):
        sys.exit()

## ICS-213 Form =================== (dual frame tab) =======================
class Tab3(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        ## Global StringVar used in both subFrames
        self.entryInc = StringVar()
        self.entryTo = StringVar()
        self.entryToPos = StringVar()
        self.entryFrom = StringVar()
        self.entryFromPos = StringVar()
        self.entrySubj = StringVar()
        self.entryDate1 = StringVar()
        self.entryTime1 = StringVar()
        self.entryApprover = StringVar()
        self.entryApprPos = StringVar()
        self.entryName = StringVar()
        self.entryNamePos = StringVar()
        self.rplyDateData = StringVar()
        self.rplyTimeData = StringVar()
        self.origMsg = StringVar()
        self.replyMsg = StringVar()
        self.loadedFileD1 = ""
        self.loadedFileT1 = ""
        self.loadedFileD2 = ""
        self.loadedFileT2 = ""
        self.loadedFlag = False
        self.colWidth = 20

        ## Set up to call the first frame = Originator    
        self._frame = None
        self.switch_frame(Tab3_Frame1)
 
    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.grid()

    ## Referenced by subframes. Do not remove
    def quitProgram(self):
        sys.exit()
      
####========================= ICS-213 Originator =============================
class Tab3_Frame1(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        ## Keep track of widgets added to frame
        self.widgets = []
        ## Init configuration dictionary
        self.commonConfData = commonConfData

        ## Frame data dictionaries
        self.origFieldsText = gv.ics213FieldsText
        self.origFieldKeys = gv.origIcs213FieldKeys
        self.ics213FormData = ics213FormData
        self.origMsg = ""
        self.result = None
        rDate = rTime = ""

        #### Load up the configuration data
        #### Necessary if a cold start
        if ics213FormData["d1"] == "":
            ## The data in the global form dict is empty
            ## fetch configuration if available
            fileNameList = [("JS8msg.cfg","*.cfg")]
            funcParam = (gv.configPath,fileNameList)
            self.result = ut.loadFormData(funcParam)

            ## ut.loadFormData returned a None object, assign default values
            if self.result is None:
                self.result = {}
                self.result["call"]=""
                self.result["phone"]=""
                self.result["name"]=""
                self.result["addr"]=""
                self.result["c-s-z"]=""
                self.result["email"]=""
                self.result["fdate"]="1"
                self.result["ftime"]="1"
                self.result["fUTC"]="0"

                self.commonConfData = self.result
                rDate, rTime = ut.dateAndTime(self.commonConfData["fdate"],self.commonConfData["ftime"],self.commonConfData["fUTC"])

            else:
                ## ut.loadFormData returned a configuration dict
                self.commonConfData = self.result
                rDate, rTime = ut.dateAndTime(self.commonConfData["fdate"],self.commonConfData["ftime"],self.commonConfData["fUTC"])

        else:
            ## a form was loaded, use the global cfg dict
            self.commonConfData = commonConfData
            rDate, rTime = ut.dateAndTime(self.commonConfData["fdate"],self.commonConfData["ftime"],self.commonConfData["fUTC"])

        ## Also need to update Date and Time before setting up GUI
        respIcs213FormData["d2"] = ics213FormData["d2"] = ics213FormData["d1"] = rDate
        respIcs213FormData["t2"] = ics213FormData["t2"] = ics213FormData["t1"] = rTime

        self.fileDropDown = StringVar()

        #### callback functions for Combobox()
        def selectFileOption(event):
            selAction = self.chooseFile.get()
            if selAction == "Save File":
                saveData()
                self.chooseFile.set('')
            elif selAction == "Load File":
                loadData()
                self.chooseFile.set('')
            elif selAction == "Clear Form":
                clearData()
                self.chooseFile.set('')
            elif selAction == "Update":
                updateData()
                self.chooseFile.set('')


        ## ICS-213 Mode Switch - Originator vs Reply
        ##
        ## For any supported forms, widgets[] is used to keep track of widgets added to the form.
        ## When changing the displayed page, widgets[] is used to destroy stored widget references
        ## there by clearing the display for the next display.
        ## Before destroying the widgets, any data is transferred to the form data dictionary
        ##
        ## Display the current mode
        self.label = Label(self, text="Orig", bg="#d8f8d8")
        self.widgets.append(self.label)
        self.label.grid(column=0,row = 0, sticky="w")

        # button object with command to replace the frame
        self.button = Button(self, text="Go to Responder Mode", command=lambda: clearForm(Tab3_Frame2))
        self.widgets.append(self.button)
        self.button.grid(column=1,row = 0, sticky="w")

        ## Get the current date and time
        self.getDtButton = Button(self, text="Get Date & Time", command=lambda:self.localGetDateTimeData(self.origDateEntry,self.origTimeEntry))
        self.widgets.append(self.getDtButton)
        self.getDtButton.grid(column=1,row = 0, sticky="e")

        ## combobox for 'file actions'
        self.comboLabel = Label(self,text = "Select =-> ")
        self.widgets.append(self.comboLabel)
        self.comboLabel.grid(column=3, row=0, sticky="w")
        self.chooseFile = ttk.Combobox(self, width=master.colWidth, textvariable=self.fileDropDown)
        self.widgets.append(self.chooseFile)
        self.chooseFile['values'] = ["Save File","Load File", "Clear Form", "Update"]
        self.chooseFile.grid(column=3, row=0, sticky="w", padx=80)
        ## NOTE: callbacks must be declared before building the combobox widget
        ## If you change any of the 'values' list entries, you must also fix the
        ## callbacks
        self.chooseFile.bind('<<ComboboxSelected>>', selectFileOption)

        ## Quit Button
        self.quitButton = Button(self, text="Quit", command=lambda:master.quitProgram())
        self.widgets.append(self.quitButton)
        self.quitButton.grid(column=3,row=0, sticky="e")
        self.quitButton.configure(bg="blue", fg="white")

        #### Text sizing variables
        normText = 42
        normText2 = 30

        incRow = 1
        ## Incident
        self.origLabelInc=Label(self, text=self.origFieldsText["inc"], anchor='w')
        self.widgets.append(self.origLabelInc)
        self.origLabelInc.grid(column=0, row=incRow, sticky = 'w')

        self.origEntryInc = Entry(self, textvariable=master.entryInc, width=normText, bg="#d8f8f8")
        self.widgets.append(self.origEntryInc)
        self.origEntryInc.grid(column=1, row=incRow, sticky='w')
        self.origEntryInc.delete(0,END)
        self.origEntryInc.insert(0,self.ics213FormData["inc"])

        ## Date Box
        self.origDateEntry =Entry(self, text=master.entryDate1, bg="#d8f8d8", width=18)
        self.widgets.append(self.origDateEntry)
        self.origDateEntry.grid(column=3, row=incRow, sticky="w")
        self.origDateEntry.delete(0,END)
        ## Need to distinguish between a blank form and a loaded form
        if master.loadedFlag:
            self.origDateEntry.insert(0,"Date: "+master.loadedFileD1) 
        else:
            self.origDateEntry.insert(0,"Date: "+ics213FormData["d1"])

        ## Time Box
        self.origTimeEntry =Entry(self, text=master.entryTime1, bg="#d8f8d8", width=18)
        self.widgets.append(self.origTimeEntry)
        self.origTimeEntry.grid(column=3, row=incRow, sticky="e")
        self.origTimeEntry.delete(0,END)
        ## Need to distinguish between a blank form and a loaded form
        if master.loadedFlag:
            self.origTimeEntry.insert(0,"Time: "+master.loadedFileT1) 
        else:
            self.origTimeEntry.insert(0,"Time: "+ics213FormData["t1"])
        

        toRow = 2
        ## To 
        self.origLabelTo=Label(self, text=self.origFieldsText["to"], anchor= 'w')
        self.widgets.append(self.origLabelTo)
        self.origLabelTo.grid(column=0, row=toRow, sticky = 'w')

        self.origEntryTo = Entry(self, textvariable=master.entryTo, width=normText, bg="#f8f8d8")
        self.widgets.append(self.origEntryTo)
        self.origEntryTo.grid(column=1, row=toRow, sticky= 'w')
        self.origEntryTo.delete(0,END)
        self.origEntryTo.insert(0,self.ics213FormData["to"])

        ## Position of 'to'
        self.origLabelToPos=Label(self, text=self.origFieldsText["p1"])
        self.widgets.append(self.origLabelToPos)
        self.origLabelToPos.grid(column=2, row=toRow, stick ='e')

        self.origEntryToPos = Entry(self, textvariable=master.entryToPos, width=normText, bg="#f8f8d8")
        self.widgets.append(self.origEntryToPos)
        self.origEntryToPos.grid(column=3, row=toRow, sticky = 'w')
        self.origEntryToPos.delete(0,END)
        self.origEntryToPos.insert(0,self.ics213FormData["p1"])

        fromRow = 3
        ##  From 
        self.origLabelFrom=Label(self, text=self.origFieldsText["fm"], anchor= 'w')
        self.widgets.append(self.origLabelFrom)
        self.origLabelFrom.grid(column=0, row=fromRow, sticky= 'w')

        self.origEntryFrom = Entry(self, textvariable=master.entryFrom, width=normText, bg="#d8f8f8")
        self.widgets.append(self.origEntryFrom)
        self.origEntryFrom.grid(column=1, row=fromRow, sticky= 'w')
        self.origEntryFrom.delete(0,END)
        self.origEntryFrom.insert(0,self.ics213FormData["fm"])

        ## Position of 'from'
        self.origLabelFromPos=Label(self, text=self.origFieldsText["p2"])
        self.widgets.append(self.origLabelFromPos)
        self.origLabelFromPos.grid(column=2, row=fromRow, sticky ='e')

        self.origEntryFromPos = Entry(self, textvariable=master.entryFromPos, width=normText, bg="#d8f8f8")
        self.widgets.append(self.origEntryFromPos)
        self.origEntryFromPos.grid(column=3, row=fromRow, sticky = 'w')
        self.origEntryFromPos.delete(0,END)
        self.origEntryFromPos.insert(0,ics213FormData["p2"])

        subjRow = 4
        ## Subject Line
        self.origLabelSubj=Label(self, text=self.origFieldsText["sb"], anchor= 'w')
        self.widgets.append(self.origLabelSubj)
        self.origLabelSubj.grid(column=0, row=subjRow, sticky = 'w')

        self.origEntrySubj = Entry(self, textvariable=master.entrySubj, width=normText, bg="#f8f8d8")
        self.widgets.append(self.origEntrySubj)
        self.origEntrySubj.grid(column=1, row=subjRow, sticky='w')
        self.origEntrySubj.delete(0,END)
        self.origEntrySubj.insert(0,ics213FormData["sb"])

        msgRow = 5
        ## Message area
        ## The Text widget allows for multi-line input and must be handled differently
        ## Text entered into this widget must use *.get() & *.set()
        self.origLabelMsg=Label(self, text=self.origFieldsText["mg"], anchor = 'w')
        self.widgets.append(self.origLabelMsg)
        self.origLabelMsg.grid(column=0, row=msgRow, sticky = 'w')

        self.origEntryMsg=Text(self)
        self.widgets.append(self.origEntryMsg)
        self.origEntryMsg.grid(column=1, row=msgRow)
        self.origEntryMsg.grid_configure(columnspan=3)
        self.origEntryMsg.configure(background="green1", wrap='word')
        self.origEntryMsg.delete(1.0,"end")
        self.origEntryMsg.insert(END,ics213FormData["mg"])
        ## update the global
        master.origMsg.set(ics213FormData["mg"])

        appRow = 7
        ## Approver
        self.origLabelApprove=Label(self, text=self.origFieldsText["s1"], anchor= 'w')
        self.widgets.append(self.origLabelApprove)
        self.origLabelApprove.grid(column=0, row=appRow, sticky= 'w')

        self.origEntryApprove = Entry(self, textvariable=master.entryApprover, width=normText, bg="#c8c8f8")
        self.widgets.append(self.origEntryApprove)
        self.origEntryApprove.grid(column=1, row=appRow, sticky= 'w')
        self.origEntryApprove.delete(0,END)
        self.origEntryApprove.insert(0,ics213FormData["s1"])

        ## Appr. Pos
        self.origLabelApprPos=Label(self, text=self.origFieldsText["p3"])
        self.widgets.append(self.origLabelApprPos)  
        self.origLabelApprPos.grid(column=2, row=appRow, stick ='e')

        self.origEntryApprPos = Entry(self, textvariable=master.entryApprPos, width=normText2, bg="#c8c8f8")
        self.widgets.append(self.origEntryApprPos)
        self.origEntryApprPos.grid(column=3, row=appRow, sticky = 'w')
        self.origEntryApprPos.delete(0,END)
        self.origEntryApprPos.insert(0,ics213FormData["p3"])

    ## destroy all widgets which were added to the current frame
    ## Then jump to the switching function
        def clearForm(frame_class):
            ## Starting 'clearForm' function.
            ## Before exiting this screen, let's save any entered data
            ## Assign only the originator data to the global dictionary
            for key in gv.origIcs213FieldKeys:
                if key == "inc":
                    ics213FormData[key] = master.entryInc.get()
                elif key == "to":
                    ics213FormData[key] = master.entryTo.get()
                elif key == "fm":
                    ics213FormData[key] = master.entryFrom.get()
                elif key == "p1":
                    ics213FormData[key] = master.entryToPos.get()
                elif key == "p2":
                    ics213FormData[key] = master.entryFromPos.get()
                elif key == "sb":
                    ics213FormData[key] = master.entrySubj.get()
                elif key == "mg":
                    ics213FormData[key] = master.origMsg.get()
                elif key == "s1":
                    ics213FormData[key] = master.entryApprover.get()
                elif key == "p3":
                     ics213FormData[key] = master.entryApprPos.get()
                elif key == "d1":
                    if master.entryDate1.get()[:6] == "Date: ":
                        ics213FormData[key] = master.entryDate1.get()[6:]
                    else:
                        ics213FormData[key] = master.entryDate1.get()
                elif key == "t1":
                    if master.entryTime1.get()[:6] == "Time: ":
                        ics213FormData[key] = master.entryTime1.get()[6:]
                    else:
                        ics213FormData[key] = master.entryTime1.get()
                
                ## transfer configuration data from local to global
                for key in gv.commonConfKeys:
                    commonConfData[key] = self.commonConfData[key]

                ## erase the widgets
                ut.clearWidgetForm(self.widgets)
                master.switch_frame(frame_class)

        def saveData():
            ## message type is hard coded to ICS-213
            ## i.e. 'file' is '213'
            for key in gv.totalIcs213Keys:
                if key == "inc":
                    ics213FormData[key] = master.entryInc.get()
                elif key == "to":
                    ics213FormData[key] = master.entryTo.get()
                elif key == "fm":
                    ics213FormData[key] = master.entryFrom.get()
                elif key == "p1":
                    ics213FormData[key] = master.entryToPos.get()
                elif key == "p2":
                    ics213FormData[key] = master.entryFromPos.get()
                elif key == "sb":
                    ics213FormData[key] = master.entrySubj.get()
                elif key == "mg":
                    ics213FormData[key] = master.origMsg.get()
                elif key == "s1":
                    ics213FormData[key] = master.entryApprover.get()
                elif key == "p3":
                    ics213FormData[key] = master.entryApprPos.get()
                elif key == "d1":
                    if master.entryDate1.get()[:6] == "Date: ":
                        ics213FormData[key] = master.entryDate1.get()[6:]
                    else:
                        ics213FormData[key] = master.entryDate1.get()
                elif key == "t1":
                    if master.entryTime1.get()[:6] == "Time: ":
                        ics213FormData[key] = master.entryTime1.get()[6:]
                    else:
                        ics213FormData[key] = master.entryTime1.get()
                ## for info of responder, transfer read data to secondary dictionary
                elif key == "rp":
                    respIcs213FormData[key] = ics213FormData[key] = master.replyMsg.get()
                elif key == "s2":
                    respIcs213FormData[key] = ics213FormData[key] = master.entryName.get()
                elif key == "p4":
                    respIcs213FormData[key] = ics213FormData[key] = master.entryNamePos.get()
                elif key == "d2":
                    if master.rplyDateData.get()[:6] == "Date: ":
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyDateData.get()[6:]
                    else:
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyDateData.get()
                elif key == "t2":
                    if master.rplyTimeData.get()[:6] == "Time: ":
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyTimeData.get()[6:]
                    else:
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyTimeData.get()
                elif key == "file":
                    ## must be accounted for. Will be needed when calling HTML template
                    respIcs213FormData[key] = ics213FormData[key] = "213"

            fileData = [("ICS-213 Forms","*.213")]
            funcParam = (gv.msgPath,fileData,ics213FormData,gv.totalIcs213Keys)
            ut.saveFormData(funcParam)
            mb.showinfo("Save","ICS-213 Form data was saved")

        def loadData():
            fileData = [("ICS-213 Forms","*.213")]
            funcParam = (gv.msgPath,fileData)
            result = ut.loadFormData(funcParam)
            ## result will be a None object if command was cancelled
            if result is not None:
                ics213FormData = result
                # Set the flag indicating that a file was loaded
                # Flag will be reset when the form is cleared
                master.loadedFlag = True
                for key in gv.totalIcs213Keys:
                    if key == "inc":
                        master.entryInc.set(ics213FormData[key])
                    elif key == "to":
                        master.entryTo.set(ics213FormData[key])
                    elif key == "fm":
                        master.entryFrom.set(ics213FormData[key])
                    elif key == "p1":
                        master.entryToPos.set(ics213FormData[key])
                    elif key == "p2":
                        master.entryFromPos.set(ics213FormData[key])
                    elif key == "sb":
                        master.entrySubj.set(ics213FormData[key])
                    elif key == "mg":
                        master.origMsg.set(ics213FormData[key])
                        self.origEntryMsg.delete(1.0,"end")
                        self.origEntryMsg.insert(END,ics213FormData["mg"])
                    elif key == "s1":
                        master.entryApprover.set(ics213FormData[key])
                    elif key == "p3":
                        master.entryApprPos.set(ics213FormData[key])
                    elif key == "d1":
                        master.loadedFileD1 = ics213FormData[key]
                        master.entryDate1.set("Date: "+ics213FormData[key])
                    elif key == "t1":
                        master.loadedFileT1 = ics213FormData[key]
                        master.entryTime1.set("Time: "+ics213FormData[key])
                    ## for info of responder, transfer read data to secondary dictionary
                    elif key == "rp":
                        respIcs213FormData[key] = ics213FormData[key]
                        master.replyMsg.set(ics213FormData[key])
                    elif key == "s2":
                        respIcs213FormData[key] = ics213FormData[key]
                    elif key == "p4":
                        respIcs213FormData[key] = ics213FormData[key]
                    elif key == "d2":
                        master.loadedFileD2 = ics213FormData[key]
                        respIcs213FormData[key] = ics213FormData[key]
                    elif key == "t2":
                        master.loadedFileT2 = ics213FormData[key]
                        respIcs213FormData[key] = ics213FormData[key]
                    elif key == "file":
                        ## must be accounted for. Will be needed when calling HTML template
                        master.tempFile = ics213FormData[key]
                        respIcs213FormData[key] = ics213FormData[key]

                mb.showinfo("Load Command","ICS-213 Form data was loaded")
            else:
                ## must have cancelled the 'load' command
                pass

        def clearData():
            for key in gv.totalIcs213Keys:
                if key == "inc":
                    ics213FormData[key] = ""
                    master.entryInc.set(ics213FormData[key])
                elif key == "to":
                    ics213FormData[key] = ""
                    master.entryTo.set(ics213FormData[key])
                elif key == "fm":
                    ics213FormData[key] = ""
                    master.entryFrom.set(ics213FormData[key])
                elif key == "p1":
                    ics213FormData[key] = ""
                    master.entryToPos.set(ics213FormData[key])
                elif key == "p2":
                    ics213FormData[key] = ""
                    master.entryFromPos.set(ics213FormData[key])
                elif key == "sb":
                    ics213FormData[key] = ""
                    master.entrySubj.set(ics213FormData[key])
                elif key == "mg":
                    ics213FormData[key] = ""
                    self.origEntryMsg.delete("1.0","end")
                    master.origMsg.set(ics213FormData[key])
                elif key == "s1":
                    ics213FormData[key] = ""
                    master.entryApprover.set(ics213FormData[key])
                elif key == "p3":
                    ics213FormData[key] = ""
                    master.entryApprPos.set(ics213FormData[key])
                elif key == "d1":
                    ics213FormData[key] = ""
                    master.loadedFileD1 = ics213FormData[key]
                    master.entryDate1.set(ics213FormData[key])
                elif key == "t1":
                    ics213FormData[key] = ""
                    master.loadedFileT1 = ics213FormData[key]
                    master.entryTime1.set(ics213FormData[key])
                ## for info of responder, transfer read data to secondary dictionary
                elif key == "rp":
                    ics213FormData[key] = ""
                    respIcs213FormData[key] = ics213FormData[key]
                    master.replyMsg.set(ics213FormData[key])
                elif key == "s2":
                    ics213FormData[key] = ""
                    master.entryName.set(ics213FormData[key])
                    respIcs213FormData[key] = ics213FormData[key]
                elif key == "p4":
                    ics213FormData[key] = ""
                    master.entryNamePos.set(ics213FormData[key])
                    respIcs213FormData[key] = ics213FormData[key]
                elif key == "d2":
                    ics213FormData[key] = ""
                    master.loadedFileD2 = ics213FormData[key]
                    respIcs213FormData[key] = ics213FormData[key]
                elif key == "t2":
                    ics213FormData[key] = ""
                    master.loadedFileT2 = ics213FormData[key]
                    respIcs213FormData[key] = ics213FormData[key]
                elif key == "file":
                    ## must be accounted for. Will be needed when calling HTML template
                    respIcs213FormData[key] = ics213FormData[key] = "213"
            master.loadedFlag = False
            ## get the current date & time
            self.localGetDateTimeData(self.origDateEntry,self.origTimeEntry)
            ## set all date & time variables to the same date and time (current)
            respIcs213FormData["d2"] = self.ics213FormData["d2"] = ics213FormData["d1"] = self.ics213FormData["d1"]
            respIcs213FormData["t2"] = self.ics213FormData["t2"] = ics213FormData["t1"] = self.ics213FormData["t1"]

        def updateData():
            for key in gv.totalIcs213Keys:
                if key == "inc":
                    ics213FormData[key] = master.entryInc.get()
                elif key == "to":
                    ics213FormData[key] = master.entryTo.get()
                elif key == "fm":
                    ics213FormData[key] = master.entryFrom.get()
                elif key == "p1":
                    ics213FormData[key] = master.entryToPos.get()
                elif key == "p2":
                    ics213FormData[key] = master.entryFromPos.get()
                elif key == "sb":
                    ics213FormData[key] = master.entrySubj.get()
                elif key == "mg":
                    ics213FormData[key] = self.origEntryMsg.get(1.0,END)
                    master.origMsg.set(ics213FormData[key])
                elif key == "s1":
                    ics213FormData[key] = master.entryApprover.get()
                elif key == "p3":
                    ics213FormData[key] = master.entryApprPos.get()
                elif key == "d1":
                    if master.entryDate1.get()[:6] == "Date: ":
                        ics213FormData[key] = master.entryDate1.get()[6:]
                    else:
                        ics213FormData[key] = master.entryDate1.get()
                elif key == "t1":
                    if master.entryTime1.get()[:6] == "Time: ":
                        ics213FormData[key] = master.entryTime1.get()[6:]
                    else:
                        ics213FormData[key] = master.entryTime1.get()
                ## for info of responder, transfer read data to secondary dictionary
                elif key == "rp":
                    respIcs213FormData[key] = ics213FormData[key] = master.replyMsg.get()
                elif key == "s2":
                    respIcs213FormData[key] = ics213FormData[key] = master.entryName.get()
                elif key == "p4":
                    respIcs213FormData[key] = ics213FormData[key] = master.entryNamePos.get()
                elif key == "d2":
                    if master.rplyDateData.get()[:6] == "Date: ":
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyDateData.get()[6:]
                    else:
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyDateData.get()
                elif key == "t2":
                    if master.rplyTimeData.get()[:6] == "Time: ":
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyTimeData.get()[6:]
                    else:
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyTimeData.get()
                elif key =="file":
                    ## must be accounted for. Will be needed when calling HTML template
                    respIcs213FormData[key] = ics213FormData[key] = "213"

            fileData = [("ICS-213 Forms","*.213")]
            funcParam = (gv.msgPath,fileData,ics213FormData,gv.totalIcs213Keys)
            ut.saveFormData(funcParam)
            mb.showinfo("Save","ICS-213 Form data was saved")

    def localGetDateTimeData(self, dateEn, timeEn):
        ## dateEn is the widget reference for the date Entry() display
        ## timeEn is the widget reference for the time Entry() display
        ## The config format data is loaded upfront
        rDate = ""
        rTime = ""
        rDate, rTime = ut.dateAndTime(self.commonConfData["fdate"],self.commonConfData["ftime"],self.commonConfData["fUTC"])
        ## update the text in the date entry box
        dateEn.delete(0,END)
        self.ics213FormData["d1"]=rDate
        dateEn.insert(0,"Date: "+ics213FormData["d1"])
        ## update the text in the time entry box
        timeEn.delete(0,END)
        self.ics213FormData["t1"]=rTime
        timeEn.insert(0,"Time: "+ics213FormData["t1"])

# second frame for Tab3
#### ============================= ICS-213 Responder ============================
class Tab3_Frame2(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        # Keep track of widgets added to frame
        self.widgets = []
        ## Frame data dictionaries
        self.rplyFieldsText = gv.ics213FieldsText
        self.rplyFieldKeys = gv.rplyIcs213FieldKeys
        self.commonConfData = gv.commonConfData
        self.ics213FormData = gv.ics213FieldsData

        #### Assume that Tab1 - Frame 1 has loaded or assigned configuration data
        ## Transfer configuration from global to local
        for key in gv.commonConfKeys:
            self.commonConfData[key] = commonConfData[key]
        
        for key in gv.rplyIcs213FieldKeys:    
            if key == "s2":
                respIcs213FormData[key] = ics213FormData[key]
                master.entryName.set(respIcs213FormData[key])
            elif key == "p4":
                respIcs213FormData[key] = ics213FormData[key]
                master.entryNamePos.set(respIcs213FormData[key])
            elif key == "d2":
                respIcs213FormData[key] = ics213FormData[key]
                master.rplyDateData.set(respIcs213FormData[key])
            elif key == "t2":
                respIcs213FormData[key] = ics213FormData[key]
                master.rplyTimeData.set(respIcs213FormData[key])
            elif key == "file":
                respIcs213FormData[key] = ics213FormData[key]

        self.fileDropDown = StringVar()

        #### callback function for Combobox()
        def selectRespFileOption(event):
            selRespAction = self.chooseRespFile.get()
            if selRespAction == "Save File":
                saveRespData()
                self.chooseRespFile.set('')
            elif selRespAction == "Clear Form":
                clearRespData()
                self.chooseRespFile.set('')
            elif selRespAction == "Update":
                updateRespData()
                self.chooseRespFile.set('')


        self.label = Label(self, text="Resp", bg="#f8d8d8")
        self.widgets.append(self.label)
        # and another button to change it back to the Originator frame
        self.button = Button(self, text="Go to Originator Mode", command=lambda: clearForm(Tab3_Frame1))
        self.widgets.append(self.button)
        self.label.grid(column=0,row=0, sticky="w")
        self.button.grid(column=1,row=0, sticky="w")

        ## Get the current date and time
        self.getDtButton = Button(self, text="Get Date & Time", command=lambda:self.getDateTimeData(self.rplyDateEntry,self.rplyTimeEntry))
        self.widgets.append(self.getDtButton)
        self.getDtButton.grid(column=1,row = 0, sticky="e")

        ## radiobutton for 'file actions'
        self.comboLabel2 = Label(self,text = "Select =-> ")
        self.widgets.append(self.comboLabel2)
        self.comboLabel2.grid(column=3, row=0, sticky="w")

        self.chooseRespFile = ttk.Combobox(self, width=master.colWidth, textvariable=self.fileDropDown)
        self.widgets.append(self.chooseRespFile)
        self.chooseRespFile['values'] = ["Save File", "Clear Form", "Update"]
        self.chooseRespFile.grid(column=3, row=0, sticky="w",padx=80)
        ## callbacks must be declared before the combobox widget
        self.chooseRespFile.bind('<<ComboboxSelected>>', selectRespFileOption)

        ## Quit button
        quitButton = Button(self, text="Quit", command=lambda:master.quitProgram())
        self.widgets.append(quitButton)
        quitButton.grid(column=3,row=0, sticky = "e")
        quitButton.configure(bg="blue", fg="white")

        #### Text sizing variable
        normText = 40

        dtRow = 1
        ## Date Box
        self.rplyDateEntry =Entry(self, textvariable=master.rplyDateData, bg="#d8f8d8", width=18)
        self.widgets.append(self.rplyDateEntry)
        self.rplyDateEntry.grid(column=3, row=dtRow, sticky="w")
        self.rplyDateEntry.delete(0,END)
        ## distinguish between blank form and loaded form
        if master.loadedFlag:
            self.rplyDateEntry.insert(0,"Date: "+master.loadedFileD2)
        else:
            self.rplyDateEntry.insert(0,"Date: "+respIcs213FormData["d2"])

        ## Time Box
        self.rplyTimeEntry =Entry(self, textvariable=master.rplyTimeData, bg="#d8f8d8", width=18)
        self.widgets.append(self.rplyTimeEntry)
        self.rplyTimeEntry.grid(column=3, row=dtRow, sticky="e")
        self.rplyTimeEntry.delete(0,END)
         ## distinguish between blank form and loaded form
        if master.loadedFlag:
            self.rplyTimeEntry.insert(0,"Time: "+master.loadedFileT2)
        else:
            self.rplyTimeEntry.insert(0,"Time: "+respIcs213FormData["t2"])

        replyRow= 2
        ## Reply area
        self.replyLabel = Label(self,text=self.rplyFieldsText['rp'])
        self.widgets.append(self.replyLabel)
        self.replyLabel.grid(column=0, row = replyRow, sticky="w")

        self.replyEntryMsg = Text(self)
        self.widgets.append(self.replyEntryMsg)
        self.replyEntryMsg.grid(column=1, row=replyRow)
        self.replyEntryMsg.grid_configure(columnspan=3)
        self.replyEntryMsg.configure(background="#f8f8d8", wrap='word')
        self.replyEntryMsg.delete(1.0,"end")
        self.replyEntryMsg.insert(END,respIcs213FormData["rp"])
        master.replyMsg.set(respIcs213FormData["rp"])

        respRow = 3
        ## Name of responder
        self.replyNameLabel = Label(self, text=self.rplyFieldsText['s2'])
        self.widgets.append(self.replyNameLabel)
        self.replyNameLabel.grid(column=0, row=respRow, sticky="w")

        self.replyEntryName = Entry(self, textvariable=master.entryName, width=normText, bg="#f8e8e8")
        self.widgets.append(self.replyEntryName)
        self.replyEntryName.grid(column=1, row=respRow, sticky="w")
        master.entryName.set(respIcs213FormData["s2"])

        ## Position of responder
        self.replyNamePosLabel = Label(self, text=self.rplyFieldsText["p4"])
        self.widgets.append(self.replyNamePosLabel)
        self.replyNamePosLabel.grid(column=2,row=respRow, sticky="w")

        self.replyNamePosEntry = Entry(self, textvariable=master.entryNamePos, width=normText, bg="#f8e8e8")
        self.widgets.append(self.replyNamePosEntry)
        self.replyNamePosEntry.grid(column=3, row=respRow, sticky="w")
        master.entryNamePos.set(respIcs213FormData["p4"])

        def clearForm(frame_class):
                ## Save any altered data
                for key in gv.rplyIcs213FieldKeys:
                    if key == "rp":
                        respIcs213FormData[key] = ics213FormData[key] = master.replyMsg.get()
                    elif key == "s2":
                        respIcs213FormData[key] = ics213FormData[key] = master.entryName.get()
                    elif key == "p4":
                        respIcs213FormData[key] = ics213FormData[key] = master.entryNamePos.get()
                    elif key == "d2":
                        respIcs213FormData[key] = ics213FormData[key]
                    elif key == "t2":
                        respIcs213FormData[key] = ics213FormData[key]
                    elif key == "file":
                        respIcs213FormData[key] = ics213FormData[key] = "213"
                ## transfer configuration data from local to global
                for key in gv.commonConfKeys:
                    commonConfData[key] = self.commonConfData[key]

                ## === Clearing widgets and switching to Originator ===
                ut.clearWidgetForm(self.widgets)
                master.switch_frame(frame_class)
        
        ## loadData() is accomplished in the Originator tab

        def saveRespData():
            for key in gv.totalIcs213Keys:
                if key == "inc":
                    ics213FormData[key] = master.entryInc.get()
                elif key == "to":
                    ics213FormData[key] = master.entryTo.get()
                elif key == "fm":
                    ics213FormData[key] = master.entryFrom.get()
                elif key == "p1":
                    ics213FormData[key] = master.entryToPos.get()
                elif key == "p2":
                    ics213FormData[key] = master.entryFromPos.get()
                elif key == "sb":
                    ics213FormData[key] = master.entrySubj.get()
                elif key == "mg":
                    ics213FormData[key] = master.origMsg.get()
                elif key == "s1":
                    ics213FormData[key] = master.entryApprover.get()
                elif key == "p3":
                    ics213FormData[key] = master.entryApprPos.get()
                elif key == "d1":
                    if master.entryDate1.get()[:6] == "Date: ":
                        ics213FormData[key] = master.entryDate1.get()[6:]
                    else:
                        ics213FormData[key] = master.entryDate1.get()
                elif key == "t1":
                    if master.entryTime1.get()[:6] == "Time: ":
                        ics213FormData[key] = master.entryTime1.get()[6:]
                    else:
                        ics213FormData[key] = master.entryTime1.get()
                ## for info of responder, transfer read data to secondary dictionary
                elif key == "rp":
                    respIcs213FormData[key] = ics213FormData[key] = master.replyMsg.get()
                elif key == "s2":
                    respIcs213FormData[key] = ics213FormData[key] = master.entryName.get()
                elif key == "p4":
                    respIcs213FormData[key] = ics213FormData[key] = master.entryNamePos.get()
                elif key == "d2":
                    if master.rplyDateData.get()[:6] == "Date: ":
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyDateData.get()[6:]
                    else:
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyDateData.get()
                elif key == "t2":
                    if master.rplyTimeData.get()[:6] == "Time: ":
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyTimeData.get()[6:]
                    else:
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyTimeData.get()
                elif key == "file":
                    respIcs213FormData[key] = ics213FormData[key] = "213"

            fileData = [("ICS-213 Forms","*.213")]
            funcParam = (gv.msgPath,fileData,ics213FormData,gv.totalIcs213Keys)
            ut.saveFormData(funcParam)
            mb.showinfo("Save","ICS-213 Form data was saved")

        def clearRespData():
            for key in gv.totalIcs213Keys:
                if key == "inc":
                    ics213FormData[key] = ""
                    master.entryInc.set(ics213FormData[key])
                elif key == "to":
                    ics213FormData[key] = ""
                    master.entryTo.set(ics213FormData[key])
                elif key == "fm":
                    ics213FormData[key] = ""
                    master.entryFrom.set(ics213FormData[key])
                elif key == "p1":
                    ics213FormData[key] = ""
                    master.entryToPos.set(ics213FormData[key])
                elif key == "p2":
                    ics213FormData[key] = ""
                    master.entryFromPos.set(ics213FormData[key])
                elif key == "sb":
                    ics213FormData[key] = ""
                    master.entrySubj.set(ics213FormData[key])
                elif key == "mg":
                    ics213FormData[key] = ""
                    self.origEntryMsg.delete("1.0","end")
                    master.origMsg.set(ics213FormData[key])
                elif key == "s1":
                    ics213FormData[key] = ""
                    master.entryApprover.set(ics213FormData[key])
                elif key == "p3":
                    ics213FormData[key] = ""
                    master.entryApprPos.set(ics213FormData[key])
                elif key == "d1":
                    ics213FormData[key] = ""
                    master.loadedFileD1 = ics213FormData[key]
                    master.entryDate1.set(ics213FormData[key])
                elif key == "t1":
                    ics213FormData[key] = ""
                    master.loadedFileT1 = ics213FormData[key]
                    master.entryTime1.set(ics213FormData[key])
                ## for info of responder, transfer read data to secondary dictionary
                elif key == "rp":
                    ics213FormData[key] = ""
                    respIcs213FormData[key] = ics213FormData[key]
                    master.replyMsg.set(ics213FormData[key])
                elif key == "s2":
                    ics213FormData[key] = ""
                    master.entryName.set(ics213FormData[key])
                    respIcs213FormData[key] = ics213FormData[key]
                elif key == "p4":
                    ics213FormData[key] = ""
                    master.entryNamePos.set(ics213FormData[key])
                    respIcs213FormData[key] = ics213FormData[key]
                elif key == "d2":
                    ics213FormData[key] = ""
                    master.loadedFileD2 = ics213FormData[key]
                    respIcs213FormData[key] = ics213FormData[key]
                elif key == "t2":
                    ics213FormData[key] = ""
                    master.loadedFileT2 = ics213FormData[key]
                    respIcs213FormData[key] = ics213FormData[key]
                elif key == "file":
                    respIcs213FormData[key] = ics213FormData[key] = "213"
            master.loadedFlag = False
            ## get the current date & time
            self.getDateTimeData(self.rplyDateEntry,self.rplyTimeEntry)
            ## set all date & time variables to the same date and time (current)
            respIcs213FormData["d2"] = self.ics213FormData["d2"] = ics213FormData["d1"] = self.ics213FormData["d1"]
            respIcs213FormData["t2"] = self.ics213FormData["t2"] = ics213FormData["t1"] = self.ics213FormData["t1"]

        def updateRespData():
            for key in gv.totalIcs213Keys:
                if key == "inc":
                    ics213FormData[key] = master.entryInc.get()
                elif key == "to":
                    ics213FormData[key] = master.entryTo.get()
                elif key == "fm":
                    ics213FormData[key] = master.entryFrom.get()
                elif key == "p1":
                    ics213FormData[key] = master.entryToPos.get()
                elif key == "p2":
                    ics213FormData[key] = master.entryFromPos.get()
                elif key == "sb":
                    ics213FormData[key] = master.entrySubj.get()
                elif key == "mg":
                    ics213FormData[key] = master.origMsg.get()
                elif key == "s1":
                    ics213FormData[key] = master.entryApprover.get()
                elif key == "p3":
                    ics213FormData[key] = master.entryApprPos.get()
                elif key == "d1":
                    if master.entryDate1.get()[:6] == "Date: ":
                        ics213FormData[key] = master.entryDate1.get()[6:]
                    else:
                        ics213FormData[key] = master.entryDate1.get()
                elif key == "t1":
                    if master.entryTime1.get()[:6] == "Time: ":
                        ics213FormData[key] = master.entryTime1.get()[6:]
                    else:
                        ics213FormData[key] = master.entryTime1.get()
                ## for info of responder, transfer read data to secondary dictionary
                elif key == "rp":
                    ics213FormData[key] = self.replyEntryMsg.get(1.0,END)
                    respIcs213FormData[key] = ics213FormData[key]
                    master.replyMsg.set(ics213FormData[key])
                elif key == "s2":
                    respIcs213FormData[key] = ics213FormData[key] = master.entryName.get()
                elif key == "p4":
                    respIcs213FormData[key] = ics213FormData[key] = master.entryNamePos.get()
                elif key == "d2":
                    if master.rplyDateData.get()[:6] == "Date: ":
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyDateData.get()[6:]
                    else:
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyDateData.get()
                elif key == "t2":
                    if master.rplyTimeData.get()[:6] == "Time: ":
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyTimeData.get()[6:]
                    else:
                        respIcs213FormData[key] = ics213FormData[key] = master.rplyTimeData.get()
                elif key == "file":
                    respIcs213FormData[key] = ics213FormData[key] = "213"

            fileData = [("ICS-213 Forms","*.213")]
            funcParam = (gv.msgPath,fileData,ics213FormData,gv.totalIcs213Keys)
            ut.saveFormData(funcParam)
            mb.showinfo("Save","ICS-213 Form data was saved")

    def getDateTimeData(self, dateEn, timeEn):
        ## dateEn is the widget reference for the date Entry() display
        ## timeEn is the widget reference for the time Entry() display
        ## The config format data is loaded upfront
        rDate = ""
        rTime = ""
        rDate, rTime = ut.dateAndTime(commonConfData["fdate"],commonConfData["ftime"],commonConfData["fUTC"])

        ## update date box
        dateEn.delete(0,END)
        respIcs213FormData["d2"] = ics213FormData["d2"]=rDate
        dateEn.insert(0,"Date: "+ics213FormData["d2"])

        ## update time box
        timeEn.delete(0,END)
        respIcs213FormData["t2"] = self.ics213FormData["t2"]=rTime
        timeEn.insert(0,"Time: "+ics213FormData["t2"])

#### ======================== End of ICS213 Form ======================================
##
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
    Root = RootApp()
    Root.geometry("800x600")
    Root.title("JS8msg")
    Root.mainloop()