##
## JS8msg is a copyrighted program written by Thomas Kocourek, N4FWD
## This program is released under the GPL v3 license
##
## Global variables
##
## Global Paths
import os
import platform

## Probably need to get system platform information
sysPlatform = platform.system()
if sysPlatform == "Linux":
    pathSep = "/"
    clearConsoleCmd = "clear"
elif sysPlatform == "Windows":
    pathSep = "\\"
    clearConsoleCmd = "cls"

configPath = os.getcwd()+pathSep+"Config"
msgPath = os.getcwd()+pathSep+"Messages"
localPath = os.getcwd()+pathSep+"Local"
templatePath = os.getcwd()+pathSep+"Templates"+pathSep
binPath = os.path.dirname(__file__)
tempPath = os.getcwd()+pathSep+"Tmp"+pathSep


##
## JS8Call APIs
txSendMessage = 'TX.SEND_MESSAGE'
rxGetCallActivity = 'RX.GET_CALL_ACTIVITY'
rxGetSelectedCall = 'RX.GET_CALL_SELECTED'
inboxGetMessages = 'INBOX.GET_MESSAGES'
inboxStoreMessage = 'INBOX.STORE_MESSAGE'
getStationID = 'STATION.GET_CALLSIGN'
getRigFreq = 'RX.GET_FREQ'
pingJS8 = 'PING'

## 
## A set of dictionaries and lists for ICS-213
## 
ics213FieldsData = {'inc':"",'to':"",'fm':"",'p1':"",'p2':"",'sb':"",'d1':"",'t1':"",'mg':"",'s1':"",'p3':"",'rp':"",'d2':"",'t2':"",'s2':"",'p4':"","file":"213"}
ics213FieldsText =  {'inc':"Inc: ",'to':"To: ",'fm':"Fm: ",'p1':"Pos.: ",'p2':"Pos.: ",'sb':"Sub.: ",'d1':"Date: ",'t1':"Time: ",'mg':"Message",'s1':"Appr. ",'p3':"Pos. ",'rp':"Reply:  ",'d2':"Date:   ",'t2':"Time:   ",'s2':"Name: ",'p4':"Pos.:","file":"ICS-213"}
origIcs213FieldKeys = ['inc','to','fm','p1','p2','sb','d1','t1','mg','s1','p3']
rplyIcs213FieldKeys = ['rp','d2','t2','s2','p4','file']
respIcs213FormData = {'rp':"",'d2':"",'t2':"",'s2':"",'p4':"",'file':""}
totalIcs213Keys = ['inc','to','p1','fm','p2','sb','d1','t1','mg','s1','p3','rp','s2','p4','d2','t2','file']
commonConfData = {'call':"", 'phone':"", 'name':"", 'addr':"", 'c-s-z':"", 'email':"", 'fdate':"", 'ftime':"", 'fUTC':""}
commonConfText = {'call':"Callsign:", 'phone':"Phone#:", 'name':"Name: ", 'addr':"Address: ", 'c-s-z':"City/St/Zip:", 'email':"Email: ", 'fdate':"Date Fmt: ", 'ftime':"Time Fmt: ", 'fUTC':"Timezone: "}
commonConfKeys = ['call','phone','name','addr', 'c-s-z','email','fdate', 'ftime','fUTC']
readConfFlag = False
readDataFlag = False

##
## some variables for facilitating the reading of messages from JS8call
##
stationCallsign = ""
messageDict = {"fm":"","mg":"","id":""}
messageDictKeys = ["fm","mg","id"]

# keep track of which form is being used
whichForm = {"form":""}
## Some path variables
## 
binPath = ""
auxPath = ""
storePath = ""
templatesPath = ""
tmpPath = ""
configurePath = ""

##
## TODO: add more dictionaries for other forms
##
