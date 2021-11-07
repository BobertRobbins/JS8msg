# JS8msg is a companion program to JS8call and adds EMCOMM form support to JS8call. 
This program was written in Python 3.8, tested in Python 3.9 and Python 3.10. JS8msg is released under the GPL v3 license. 
For Linux, you need a minimum level Python of 3.8 installed on your system. For Windows, no need to install Python as Python is compiled into JS8msg.

The software should be considered BETA. Rewrites will occur as the code is made more supportive of multi-platform.

Directory structure:<br>
For a Linux installation:<br>
  home directory > JS8msg > Bin (Python scripts go here)<br>
  JS8msg > Doc (documentation files)<br>
  JS8msg > Config (holds the configuration file)<br>
  JS8msg > Local (holds icon image, *.desktop file, *.sh starter shell)<br>
  JS8msg > Messages (hold locally created messages as well as downloaded messages)<br>
  JS8msg > HtmlTemplates (holds HTML templates for displaying a form on the web browser)<br>
  JS8msg > Tmp (temporary file storage)<br>
<br>
Quick Guide for first time installation in Linux:<br>
  Download the zipfile from https://github.com/tkocou/JS8msg. Unzip the file in your home directory. Open a terminal window and type in:<br>
    cd JS8msg<br>
    ./Bin/js8msg.py<br>
  The program will automatically create missing directories as well as set up a clickable desktop icon.
  Since the configuration file has not been created yet, just click on "Cancel" and then the Quit button. Afterwards, just click on the desktop icon to start JS8msg.
<br><br>
Quick Guide for first time installation in Windows 10:<br>
  Download the <b>JS8msg.exe</b> file from  https://github.com/tkocou/JS8msg
  Copy the <b>JS8msg.exe file</b> to your home directory and execute it. The program will build the <b>"Doc, Config, Local, Messages, HtmlTemplates and Tmp"</b> directories and the needed files before starting the main program.
  Since the configuration file has not been created yet, just click on "Cancel" and then the Quit button. Afterwards, just click on the desktop icon to start JS8msg.
