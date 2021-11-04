##
## JS8msg is a copyrighted program written by Thomas Kocourek, N4FWD
## This program is released under the GPL v3 license
##
## Global variables
##
## Global Paths
import os
import sys
import platform
import shutil
from tkinter import messagebox as mb

def setup():
    ## Get the true home dir for multi-platform
    ## Should return absolute path regardless of OS
    homeDir = os.path.expanduser('~')

    ## create the needed paths
    js8Path = os.path.join(homeDir,"JS8msg")
    localPath = os.path.join(js8Path,"Local")
    desktopDir = os.path.join(homeDir,"Desktop")
    localBinDir = os.path.join(homeDir,"bin")

    ## Check if JS8msg is in the home directory
    cwd = os.getcwd()
    if cwd != js8Path:
        mb.showinfo("ERROR!!", "JS8msg is not in your home directory. Please copy JS8msg to your home directory.")
        sys.exit()

    ## Get system platform information
    ## and copy over icons if missing
    sysPlatform = platform.system()
    if sysPlatform == "Linux":
        iFile = "JS8msg.desktop"
    elif sysPlatform == "Windows":
        iFile = "JS8msg.lnk"
    iconFile = os.path.join(localPath,iFile)
    shellFile = os.path.join(localPath,"js8msg.sh")
    iconCheck = os.path.join(desktopDir,iFile)
    linuxShell = os.path.join(localBinDir,"js8msg.sh")
    if not os.path.exists(iconCheck):
        shutil.copy2(iconFile,desktopDir)
    if not os.path.exists(linuxShell):
        shutil.copy2(shellFile,localBinDir)
    return


      


