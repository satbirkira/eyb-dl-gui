#Imports
from tkinter import *
import webbrowser
import os
import array
import tkinter.messagebox
from tkinter import ttk
import re
import codecs
import sys
import datetime
import subprocess
import time
from time import gmtime, strftime
from constants import State, Format, Quality, titleFormat, videoState
from model import Model
import view

# Initial Window Widget
root = Tk()
root.title("Easy Youtube Bookmark Downloader 3.0 -- By Satbir Saini")
root.minsize(700,350)
# Open View
mainModel = Model()
mainView = view.View(root, mainModel)
mainModel.addView(mainView)
# Enter GUI Event Loop
root.mainloop()
