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
from subprocess import PIPE, Popen
from threading  import Thread, Timer
import datetime
import subprocess
import time
from time import gmtime, strftime
from constants import State, Format, Quality, titleFormat, videoState
from queue import Queue, Empty



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

    #make youtube-dl instance avaliable
    youtube_dl_process = None
    youtube_dl_stdout_queue = None
    youtube_dl_stdout_thread = None
    youtube_dl_stdout_stdout_timer = None

    ON_POSIX = 'posix' in sys.builtin_module_names



    def debug(self):
        print("==================================")
        print("File Path = " + self.getFilePath())
        print("Output Path = " + self.getOutputPath())
        print("Video Format = " + Format.toString[self.getOutputFormat()])
        print("Title Format = " + titleFormat.toString[self.getOutputTitleFormat()])
        print("Quality = " + Quality.toString[self.getOutputQuality()])
        print("Status = " + State.toString[self.getStatus()])
        print("Current Video ID = " + str(self.getCurrentVideoID()) +". Total # Videos: "+ str(self.numberOfVideos()))
        print("Video Info = ")
        print(self.currentVideoInformation())
        print("==================================")        

    def getFilePath(self):
        return self.filepath
    def setFilePath(self, path):
        self.filepath = path
        self.updateAllViews()
        
    def getOutputPath(self):
        return self.outputPath
    def setOutputPath(self, path):
        self.outputPath = path
        self.updateAllViews()

    def getOutputFormat(self):
        return self.outputFormat
    def setOutputFormat(self, outputFormat):
        self.outputFormat = outputFormat
        self.updateAllViews()
        

    def getOutputTitleFormat(self):
        return self.output_title_format
    def setOutputTitleFormat(self, titleFormat):
        self.output_title_format = titleFormat
        self.updateAllViews()

    def getOutputQuality(self):
        return self.outputQuality
    def setOutputQuality(self, quality):
        self.outputQuality = quality
        self.updateAllViews()

    def getStatus(self):
        return self.program_status
    def setStatus(self, status):
        self.program_status = status


    def numberOfVideos(self):
        return len(self.videos)

    def getCurrentVideoID(self):
        return self.current_video

    def currentVideoInformation(self):
        i = self.current_video
        if i > self.numberOfVideos()-1 or i < 0:
            return {}
        else:
            return self.videos[i]
    

    def __init__(self):
        self.setOutputPath(os.getcwd())
        self.setStatus(State.NO_OPEN_FILE)
        
    def addView(self, view):
        self.views.append(view)
        view.update()

    def updateAllViews(self):
        self.debug()
        for view in self.views:
            view.update()

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
                #if we could not extract bookmarks, simply scan for youtube videos
                if(len(videos) == 0):
                    regex = re.compile('v=([^&#\n]*)')
                    r = regex.findall(bookmark_file)
                    videos = regex.findall(bookmark_file)
                    #fill with empty title
                    print(videos)
                    for i in range(0, len(videos)):
                        videos[i] = (videos[i], "")
                    if(len(videos) > 0):
                        #set title to be determined by youtube
                        self.setOutputTitleFormat(titleFormat.USE_YOUTUBE_TITLE)
                #remove duplicate videos and create proper links
                newlist = []
                newlist_urls = []
                id = 0;
                for video in videos:
                    formated_title = video[1].replace("\\", " ")#replace single slash
                    formated_title = formated_title.replace("?", " ")
                    formated_title = formated_title.replace(".", " ")
                    formated_title = formated_title.replace("|", " ")
                    formated_title = formated_title.replace("*", " ")
                    formated_title = formated_title.replace("<", " ")
                    formated_title = formated_title.replace(">", " ")
                    formated_title = formated_title.replace("\"", " ")
                    formated_title = formated_title.replace("/", " ")
                    formated_title = formated_title.replace(":", " ")
                    formated_title = formated_title.strip()
                    if(len(formated_title) > 255):
                            formated_title = formated_title[0:254]
                    if(formated_title == ""):
                        formated_title = "Title Avaliable When Downloading [" + str(id) + "]"
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
                            id += 1
                #store fixed video list
                self.videos = newlist
                if self.numberOfVideos() == 0:
                    self.setStatus(State.EMPTY_FILE)
                    self.updateAllViews()
                    self.setStatus(old_status)
                else:
                    self.setStatus(State.FILE_OPENED)
        self.updateAllViews()
        
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

    #WORK HERE

    def startDownloading(self):
        if self.validateOutputPath():
            if self.getStatus() == State.FILE_OPENED:
                self.setStatus(State.DOWNLOADING)
                self.downloadCurrentVideo()
                self.updateAllViews()
            elif self.getStatus() == State.DOWNLOADING:
                self.setStatus(State.FILE_OPENED)
                self.updateAllViews()

    def validateOutputPath(self):
        old_status = self.getStatus()
        if not (os.path.isdir(self.getOutputPath())):
            self.setStatus(State.INVALID_OUTPUT_PATH)
            self.updateAllViews()
            self.setStatus(old_status)
            self.updateAllViews()
            return False
        else:
            return True


    def videoStatus(self, i):
        return self.videos[i]["Info"]["Status"]

    def changeVideoStatus(self, i, status):
        self.videos[i]["Info"]["Status"] = status
        
    def cancelVideo(self):
        #kill thread, clear queue, terminate process
        self.youtube_dl_stdout_stdout_timer.stop()
        self.youtube_dl_stdout_thread.stop()
        self.youtube_dl_process.terminate()
        self.youtube_dl_stdout_queue.clear()
        #set them to null
        self.youtube_dl_stdout_thread = None
        self.youtube_dl_process = None
        self.youtube_dl_stdout_queue = None
        self.youtube_dl_stdout_stdout_timer = None
        #update video meta info
        self.videos[self.current_video]["Info"]["Status"] = videoState.QUEUED
        self.videos[self.current_video]["Info"]["Percent"] = 0
        self.videos[self.current_video]["Info"]["Size"] = 0
        self.videos[self.current_video]["Info"]["Speed"] = 0
        self.videos[self.current_video]["Info"]["remainingTime"] = 0
        

    def downloadCurrentVideo(self):
        #make sure the refrence is null
        youtube_dl_instance = None
        current_video_info = self.currentVideoInformation()
        
        #set program name
        input_command = []
        input_command.extend(["youtube-dl"])
        
        
        #set format and quality
        if(self.getOutputFormat()==Format.FLV or self.getOutputFormat()==Format.MP4):
            if(self.getOutputQuality()==Quality.HIGH):
                input_command.extend(["--max-quality"])
            elif(self.getOutputQuality()==Quality.NORMAL):
                input_command.extend(["--format"])
            input_command.extend([Format.toString[self.getOutputFormat()]])
        elif(self.getOutputFormat()==Format.MP3 or self.getOutputFormat()==Format.WAV):
            input_command.extend(["--extract-audio", "--audio-format", Format.toString[self.getOutputFormat()]])
            if(self.getOutputQuality()==Quality.NORMAL):
                input_command.extend(["--audio-quality 5"])
            elif(self.getOutputQuality()==Quality.HIGH):
                input_command.extend(["--audio-quality 0"])
        
    
        #add flags and output path
        input_command.extend(["--continue", "--ignore-errors", "--no-overwrites", "--no-check-certificate", "-o"])
       

        #set output title
        if(self.getOutputTitleFormat() == titleFormat.USE_BOOKMARK_TITLE):
            input_command.extend([ "\"" + self.getOutputPath() + "\\" + current_video_info["Title"] + ".%(ext)s\""])
            
        elif(self.getOutputTitleFormat() == titleFormat.USE_YOUTUBE_TITLE):
            input_command.extend([ "\"" + self.getOutputPath() + "\\" + "%(title)s.%(ext)s\""])
            
        #add the video url and a restrict filename tag
        input_command.extend(["http://" + current_video_info["Url"], "--restrict-filenames"])
        
                
        print(input_command)
        #http://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python

        #ope thread and get stdout asynch
        self.youtube_dl_process = Popen(input_command, stdout=PIPE, stderr=PIPE, bufsize=1, close_fds=self.ON_POSIX)
        self.youtube_dl_stdout_queue = Queue()
        self.youtube_dl_stdout_thread = Thread(target=self.enqueue_output, args=(self.youtube_dl_process.stdout,
                                                                                 self.youtube_dl_process.stderr,
                                                                                 self.youtube_dl_stdout_queue))
        self.youtube_dl_stdout_thread.daemon = True # thread dies with the program
        
        self.youtube_dl_stdout_stdout_timer = Timer(0.25, self.update_current_video_info_timer)
        self.update_current_video_info_timer()
        self.youtube_dl_stdout_thread.start()

    def update_current_video_info_timer(self):
        if self.getStatus() == State.DOWNLOADING:
            # read line without blocking
            try:  line = self.youtube_dl_stdout_queue.get_nowait() # or q.get(timeout=.1)
            except Empty:
                print('no output yet')
                self.youtube_dl_stdout_stdout_timer = Timer(0.25, self.update_current_video_info_timer)
                self.youtube_dl_stdout_stdout_timer.start()
            else:
                print(line)
                self.youtube_dl_stdout_stdout_timer = Timer(0.25, self.update_current_video_info_timer)
                self.youtube_dl_stdout_stdout_timer.start()
        #if it has started downloading timer set it to 1

            
        

    #add stdout lines to queue
    def enqueue_output(self, out, err, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()
        for line in iter(err.readline, b''):
            queue.put(line)
        err.close()


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
