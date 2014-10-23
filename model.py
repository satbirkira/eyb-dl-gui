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



#Program Class
class Model():

    #bookmark info
    filepath = ""
    videos=[]
    program_status = State.NO_OPEN_FILE
    output_title_format = titleFormat.USE_BOOKMARK_TITLE

    #mvc views
    views =[]

    #default HQ FLV
    outputFormat = Format.FLV
    outputQuality = Quality.NORMAL

    #video downloading info
    current_video = 0
    outputPath = ""

    def getFilePath(self):
        return self.filepath
    def setFilePath(self, path):
        print(path)
        self.filepath = path
        
    def getOutputPath(self):
        return self.outputPath
    def setOutputPath(self, path):
        self.outputPath = path

    def getOutputFormat(self):
        return self.outputFormat
    def setOutputFormat(self, outputFormat):
        self.outputFormat = outputFormat

    def getOutputTitleFormat(self):
        return self.output_title_format
    def setOutputTitleFormat(self, titleFormat):
        self.output_title_format = titleFormat

    def getOutputQuality(self):
        return self.outputQuality
    def setOutputQuality(self, quality):
        self.outputQuality = quality


    def getStatus(self):
        return self.program_status
    def setStatus(self, status):
        self.program_status = status


    def numberOfVideos(self):
        return len(self.videos)

    def currentVideoStatus(self):
        i = self.current_video
        return self.videos[i]["Info"]["Status"]
    

    def __init__(self):
        self.setOutputPath(os.getcwd())
        self.setStatus(State.NO_OPEN_FILE)
        
    def addView(self, view):
        self.views.append(view)
        view.update()

    def updateAllViews(self):
        print ("here1")
        for view in self.views:
            view.update()
            print ("here2")

    def say_clicked(self):
         print ("clicked!")

    def loadBookmark(self, filepath):
        if self.getStatus() not in [State.DOWNLOADING, State.OPENING_FILE, State.UPDATING]:
            #get bookmark filepath
            self.setFilePath(filepath)
            old_status = self.getStatus()
            try:
                check_file = open(self.getFilePath())
                print ("File opened successfully.")
                check_file.close()
            except:
                self.setStatus(State.EMPTY_FILE)
                self.updateAllViews()
                self.setStatus(old_status)
            else:
                #load the bookmark using regex
                self.setStatus(State.OPENING_FILE)
                self.updateAllViews()
                content_file = codecs.open(self.getFilePath(), 'r', 'utf-8')
                print ("Reading from bookmarks.html ..")
                bookmark_file = content_file.read()
                print ("Applying Regular Expression ..")
                regex = re.compile('.*<DT><A\sHREF=".*www\.youtube\.com/watch\?.*v=([^&#"]*)\S*".*>(.*)</A>\n?')
                r = regex.search(bookmark_file)
                videos = regex.findall(bookmark_file)
                #remove duplicate videos and create proper links
                newlist = []
                newlist_urls = []
                for video in videos:
                    formated_title = video[1].replace("\\", " ")#replace single slash
                    formated_title = video[1].replace("?", " ")
                    formated_title = video[1].replace(".", " ")
                    formated_title = video[1].replace("|", " ")
                    formated_title = video[1].replace("*", " ")
                    formated_title = video[1].replace("<", " ")
                    formated_title = video[1].replace(">", " ")
                    formated_title = video[1].replace("\"", " ")
                    formated_title = video[1].replace("/", " ")
                    formated_title = video[1].replace(":", " ")
                    if(len(formated_title) > 255):
                            formated_title = formated_title[0:254]
                    formated_video = {"Url": "www.youtube.com/watch?v=" + video[0],
                                      "Title": formated_title,
                                      "Info": {
                                                "Status": videoState.QUEUED,
                                                "Percent": 0,
                                                "Size": 0,
                                                "Speed": 0,
                                                "remainingTime": 0}
                                      }
                    if formated_video["Url"] not in newlist_urls:
                            newlist_urls.append(formated_video["Url"])
                            newlist.append(formated_video)
                #store fixed video list
                self.videos = newlist
                if self.numberOfVideos() == 0:
                    self.setStatus(State.EMPTY_FILE)
                    self.updateAllViews()
                    self.setStatus(old_status)
                else:
                    self.setStatus(State.FILE_OPENED)
                print ("here")
            self.updateAllViews()
            print ("here")
    
    def updateYTDL(self):
        if self.getStatus() not in [State.DOWNLOADING, State.OPENING_FILE, State.UPDATING]:
            print(os.getcwd()+"\youtube-dl.exe --update")
            old_status = self.getStatus()
            self.setStatus(State.UPDATING)
            self.updateAllViews()
            update_youtube_dl = subprocess.Popen(os.getcwd()+"\youtube-dl.exe --update",
                                                 stderr=subprocess.PIPE,
                                                 stdout=subprocess.PIPE,
                                                 universal_newlines=True)
            err = update_youtube_dl.communicate()
            out = update_youtube_dl.communicate()[0]
            errcode = update_youtube_dl.returncode
            print(out)
            if len(err[1].strip()) !=0  or re.search("ERROR:", out):
                print ("Standard error of youtube-dl:")
                print (err[1])
                print ("Using current version of youtube-dl ..")
                self.setStatus(State.YTDL_UPDATE_FAIL)
                self.updateAllViews()
            else:
                self.setStatus(State.YTDL_UPDATE_SUCCESS)
                self.updateAllViews()
            self.setStatus(old_status)
            self.updateAllViews()
        

    def startDownloading(self):
        if self.getStatus() == State.FILE_OPENED:
            print ("DOWNLOADING!")
            self.setStatus(State.DOWNLOADING)
            self.updateAllViews()
        elif self.getStatus() == State.DOWNLOADING:
            print ("PAUSED!")
            self.setStatus(State.FILE_OPENED)
            self.updateAllViews()


    def videoStatus(self, i):
        return self.videos[i]["Info"]["Status"]

    def changeVideoStatus(self, i, status):
        self.videos[i]["Info"]["Status"] = status
        
    def cancelVideo(self):
        #kill thread, update video meta info, advance counter
        #call thread to download current video
        return None

    def downloadCurrentVideo(self):
        pass

    def removeItemFromList(self, i):
        i = int(i)
        if self.videoStatus(i) == videoState.QUEUED:
            self.changeVideoStatus(i, videoState.SKIPPED)
            self.updateAllViews() #for some reason, this must be repeated at every condition
        elif self.videoStatus(i)== videoState.DOWNLOADING or self.videoStatus(i) == videoState.CONVERTING:
            self.cancelVideo()
            self.changeVideoStatus(i, videoState.CANCELLED)
            self.updateAllViews()
        
    def queueItemFromList(self, i):
        i = int(i)
        if self.videoStatus(i) == videoState.SKIPPED:
            self.changeVideoStatus(i, videoState.QUEUED)
        self.updateAllViews()