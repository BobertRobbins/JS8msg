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
    keyList = ['apidoc','copydoc','installdoc','guidedoc','deindoc']
    fileList = {'apidoc':"API.pdf",'copydoc':"COPYING",'installdoc':"INSTALL",'guidedoc':"JS8msg Guide.pdf",'deindoc':"DEINSTALL"}

    keyList2 = ['ldesk','lshell','wdesk','licon','wicon']
    fileList2 = {'ldesk':"JS8msg.desktop",'lshell':"js8msg",'wdesk':"JS8msg.lnk",'licon':"js8msg.png",'wicon':"js8msg.ico"}

    keyList3 = ['25a','205','213','214']
    fileList3 = {'25a':"ics205a_template.html",'205':"ics205_template.html",'213':"ics213_template.html",'214':"ics214_templates.html"}

    sysPlatform = platform.system()

    ## Get the true home dir for multi-platform
    ## Should return absolute path regardless of OS
    homeDir = os.path.expanduser('~')
    os.chdir(homeDir)
    ## Path to Desktop
    desktopDir = os.path.join(homeDir,"Desktop")

    if sysPlatform == "Windows":
        extDocumentPath = os.path.join(homeDir,"Doc")
        extLocalPath = os.path.join(homeDir,"Local")
        extTemplatePath = os.path.join(homeDir,"HtmlTemplates")

        try:
            os.mkdir(extDocumentPath)
            print("Created directory 'Doc'.")
        except: ## directory already exists, do nothing
            pass
        try:
            os.mkdir(extLocalPath)
            print("Created directory 'Local'.")
        except: ## directory already exists, do nothing
            pass
        try:
            os.mkdir(extTemplatePath)
            print("Created directory 'HtmlTemplates'.")
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
            fileName = os.path.join(extTemplatePath,fileList3[key])
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

        iFile = "JS8msg.lnk"
    
        iconFile = os.path.join(extLocalPath,iFile)
        iconCheck = os.path.join(desktopDir,iFile)
        if not os.path.exists(iconCheck):
            shutil.copy2(iconFile,desktopDir)

    if sysPlatform == "Linux":
        iFile = "JS8msg.desktop"
        linuxLocalBinDir = os.path.join(homeDir,"bin")
        linuxShell = os.path.join(linuxLocalBinDir,"js8msg.sh")
        linuxShellTunc = os.path.join(linuxLocalBinDir,"js8msg")
        linuxLocalPath = os.path.join(homeDir,"JS8msg/Local")
        linuxLocalDirFile = os.path.join(linuxLocalPath,"js8msg.sh")
        iconCheck = os.path.join(desktopDir,iFile)
        iconFile = os.path.join(linuxLocalPath,iFile)
        try:
            os.mkdir(linuxLocalBinDir)
        except: ## directory already exists, do nothing
            pass
        if not os.path.exists(linuxShell):
            shutil.copy2(linuxLocalDirFile,linuxLocalBinDir)
            os.chmod(linuxShell,0o755)
            os.rename(linuxShell,linuxShellTunc)
        if not os.path.exists(iconCheck):
            shutil.copy2(iconFile,desktopDir)
            os.chmod(iconCheck,0o755)

    return
