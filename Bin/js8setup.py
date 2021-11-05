##
## JS8msg is a copyrighted program written by Thomas Kocourek, N4FWD
## This program is released under the GPL v3 license
##
import os
import platform
import shutil
import base64
import bz2
import documents as doc
import locals as lc
import template as tp

def setup():
    keyList = ['apidoc','copydoc','installdoc','guidedoc']
    fileList = {'apidoc':"API.pdf",'copydoc':"COPYING",'installdoc':"INSTALL",'guidedoc':"JS8msg Guide.pdf"}

    keyList2 = ['ldesk','lshell','wdesk','licon','wicon']
    fileList2 = {'ldesk':"JS8msg.desktop",'lshell':"js8msg",'wdesk':"JS8msg.lnk",'licon':"js8msg.png",'wicon':"js8msg.ico"}

    keyList3 = ['25a','205','213','214']
    fileList3 = {'25a':"ics205a_template.html",'205':"ics205_template.html",'213':"ics213_template.html",'214':"ics214_templates.html"}

    sysPlatform = platform.system()

    ## Get the true home dir for multi-platform
    ## Should return absolute path regardless of OS
    homeDir = os.path.expanduser('~')

    extDocumentPath = os.path.join(homeDir,"Doc")
    extLocalPath = os.path.join(homeDir,"Local")
    extTemplatePath = os.path.join(homeDir,"Templates")
    desktopDir = os.path.join(homeDir,"Desktop")
    linuxLocalBinDir = os.path.join(homeDir,"bin")

    try:
            os.mkdir(extDocumentPath)
    except: ## directory already exists, do nothing
            pass
    try:
            os.mkdir(extLocalPath)
    except: ## directory already exists, do nothing
            pass
    try:
            os.mkdir(extTemplatePath)
    except: ## directory already exists, do nothing
            pass
    
    for key in keyList:
        fileName = os.path.join(extDocumentPath,fileList[key])
        ## if the file exists, remove and replace it (auto-upgrade of file)
        if os.path.exists(fileName):
            os.remove(fileName)
        stringData = doc.docArray[key]
        byteData = bytes(stringData,'utf-8')
        decodedData = base64.b64decode(byteData)
        rawArray = bz2.decompress(decodedData)
        print("Updating or creating document %s." % fileName)
        with open(fileName,"wb") as f:
            f.write(rawArray)

    for key in keyList2:
        fileName = os.path.join(extLocalPath,fileList2[key])
        ## if the file exists, remove and replace it (auto-upgrade of file)
        if os.path.exists(fileName):
            os.remove(fileName)
        stringData = lc.localArray[key]
        byteData = bytes(stringData,'utf-8')
        decodedData = base64.b64decode(byteData)
        rawArray = bz2.decompress(decodedData)
        print("Updating or creating file %s." % fileName)
        with open(fileName,"wb") as f:
            f.write(rawArray)

    for key in keyList3:
        fileName = os.path.join(extLocalPath,fileList3[key])
        ## if the file exists, remove and replace it (auto-upgrade of file)
        if os.path.exists(fileName):
            os.remove(fileName)
        stringData = tp.templateArray[key]
        byteData = bytes(stringData,'utf-8')
        decodedData = base64.b64decode(byteData)
        rawArray = bz2.decompress(decodedData)
        print("Updating or creating template %s." % fileName)
        with open(fileName,"wb") as f:
            f.write(rawArray)

    ## Get system platform information
    ## and copy over icons if missing
    if sysPlatform == "Linux":
        iFile = "JS8msg.desktop"
    elif sysPlatform == "Windows":
        iFile = "JS8msg.lnk"
    iconFile = os.path.join(extLocalPath,iFile)
    iconCheck = os.path.join(desktopDir,iFile)
    if not os.path.exists(iconCheck):
        shutil.copy2(iconFile,desktopDir)
    shellFile = os.path.join(extLocalPath,"js8msg.sh")
    linuxShell = os.path.join(linuxLocalBinDir,"js8msg.sh")
    if sysPlatform == "Linux":
        if not os.path.exists(linuxShell):
            shutil.copy2(shellFile,linuxLocalBinDir)

    return


      


