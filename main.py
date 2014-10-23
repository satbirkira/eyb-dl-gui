#Imports
from tkinter import *
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