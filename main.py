#Imports
from tkinter import *
from constants import State, Format, Quality, titleFormat, videoState
from model import Model
import view
import os

# Initial Window Widget
root = Tk()
os.environ["PATH"] = os.getcwd()
# Open View
mainModel = Model()
mainView = view.View(root, mainModel)
mainModel.addView(mainView)
# Enter GUI Event Loop
root.mainloop()
