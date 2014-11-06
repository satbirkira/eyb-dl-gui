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
from time import strftime
from constants import State, Format, Quality, titleFormat, videoState
from queue import Queue, Empty

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
    youtube_dl_thread = None
    youtube_dl_stdout_queue = None
    youtube_dl_stderr_queue = None
    youtube_dl_output_timer = None

    #misc variables
    ON_POSIX = 'posix' in sys.builtin_module_names
    error_log_file_name = None

    def __init__(self):
        self.setOutputPath(os.getcwd())
        self.setStatus(State.NO_OPEN_FILE)

    '''
        MVC Functions
    '''
        
    def addView(self, view):
        self.views.append(view)
        view.update()

    def updateAllViews(self):
        #self.debug()
        for view in self.views:
            view.update()

    '''
        Getters and Setters
    '''
   
    def getFilePath(self):
        return self.filepath
    
    def setFilePath(self, path):
        if self.getStatus() not in [State.DOWNLOADING, State.OPENING_FILE, State.UPDATING]:
            self.filepath = path
            self.updateAllViews()
        
    def getOutputPath(self):
        return self.outputPath
    
    def setOutputPath(self, path):
        if self.getStatus() not in [State.DOWNLOADING, State.OPENING_FILE, State.UPDATING]:
            self.outputPath = path
            self.updateAllViews()

    def getOutputFormat(self):
        return self.outputFormat
    
    def setOutputFormat(self, outputFormat):
        if self.getStatus() not in [State.DOWNLOADING, State.OPENING_FILE, State.UPDATING]:
            if outputFormat <= self.getUpperBoundOfConstant(Format)-1 and outputFormat >= 0:
                self.outputFormat = outputFormat
                self.updateAllViews()
        
    def getOutputTitleFormat(self):
        return self.output_title_format
    
    def setOutputTitleFormat(self, outputTitleFormat):
        if self.getStatus() not in [State.DOWNLOADING, State.UPDATING]:
            if outputTitleFormat <= self.getUpperBoundOfConstant(titleFormat)-1 and outputTitleFormat >= 0:
                self.output_title_format = outputTitleFormat
                self.updateAllViews()

    def getOutputQuality(self):
        return self.outputQuality
    
    def setOutputQuality(self, quality):
        if self.getStatus() not in [State.DOWNLOADING, State.OPENING_FILE, State.UPDATING]:
            if quality <= self.getUpperBoundOfConstant(Quality)-1 and quality >= 0:
                self.outputQuality = quality
                self.updateAllViews()

    def getStatus(self):
        return self.program_status
    
    def setStatus(self, status):
        if status <= self.getUpperBoundOfConstant(State)-1 and status >= 0:
            self.program_status = status

    def videoStatus(self, i):
        if i <= self.numberOfVideos()-1 and i >= 0:
            return self.videos[i]["Info"]["Status"]

    def changeVideoStatus(self, i, status):
        if i <= self.numberOfVideos()-1 and i >= 0:
            self.videos[i]["Info"]["Status"] = status

    def getVideoList(self):
        return self.videos
    
    def setVideoList(self, videoList):
        self.videos = videoList

    def removeItemFromList(self, i):
        i = int(i)
        if i <= self.numberOfVideos()-1 and i >= 0:
            if self.videoStatus(i) == videoState.QUEUED:
                self.changeVideoStatus(i, videoState.SKIPPED)
                self.updateAllViews() #for some reason, this must be repeated at every condition
            elif self.videoStatus(i)== videoState.DOWNLOADING:
                self.clean_up_current_video(videoState.CANCELLED)
                self.updateAllViews()
        
    def queueItemFromList(self, i):
        i = int(i)
        if i <= self.numberOfVideos()-1 and i >= 0:
            if self.videoStatus(i) == videoState.SKIPPED:
                self.changeVideoStatus(i, videoState.QUEUED)
            self.updateAllViews()

    def getUpperBoundOfConstant(self, CONSTANT):
        return len(CONSTANT.toString)

    '''
        Information Pertaining The Current Video
    '''

    def getCurrentVideoID(self):
        return self.current_video

    def setCurrentVideoID(self, i):
        self.current_video = i

    def numberOfVideos(self):
        return len(self.videos)

    def currentVideoData(self):
        i = self.current_video
        if i > self.numberOfVideos()-1 or i < 0:
            return {}
        else:
            return self.videos[i]
    
    def advance_current_video(self):
        self.current_video += 1

    def clean_up_current_video(self, videoStateGiven):
        self.currentVideoData()["Info"]["Status"] = videoStateGiven
        self.currentVideoData()["Info"]["Percent"] = 0
        self.currentVideoData()["Info"]["Size"] = 0
        self.currentVideoData()["Info"]["Speed"] = 0
        self.currentVideoData()["Info"]["remainingTime"] = 0
        self.updateAllViews()

    '''
        Loading Video From File
    '''

    def loadBookmark(self, filepath):
        if self.getStatus() not in [State.DOWNLOADING, State.OPENING_FILE, State.UPDATING]:
            #get bookmark filepath
            self.setFilePath(filepath)
            old_status = self.getStatus()
            try:
                check_file = open(self.getFilePath())
                #print ("File opened successfully.")
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
                #print ("Reading from bookmarks.html ..")
                bookmark_file = content_file.read()
                content_file.close()
                #print ("Applying Regular Expression ..")
                regex = re.compile('.*<DT><A\sHREF=".*www\.youtube\.com/watch\?.*v=([^&#"]*)\S*".*>(.*)</A>\n?')
                r = regex.search(bookmark_file)
                videos = regex.findall(bookmark_file)
                #if we could not extract bookmarks, simply scan for youtube videos
                if(len(videos) == 0):
                    regex = re.compile('v=([^&#\n]*)')
                    videos = regex.findall(bookmark_file)
                    #fill with empty title
                    #print(videos)
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
                self.setVideoList(newlist)
                if self.numberOfVideos() == 0:
                    self.setStatus(State.EMPTY_FILE)
                    self.updateAllViews()
                    self.setStatus(old_status)
                else:
                    self.setStatus(State.FILE_OPENED)
        self.updateAllViews()

    '''
        Update youtube-dl
    '''
        
    def updateYTDL(self):
        if self.getStatus() not in [State.DOWNLOADING, State.OPENING_FILE, State.UPDATING]:
            #print(os.getcwd()+"\youtube-dl.exe --update")
            old_status = self.getStatus()
            self.setStatus(State.UPDATING)
            self.updateAllViews()
            update_youtube_dl = subprocess.Popen(os.getcwd()+"\youtube-dl --update",
                                                 stderr=subprocess.PIPE,
                                                 stdout=subprocess.PIPE,
                                                 universal_newlines=True)
            err = update_youtube_dl.communicate()
            out = update_youtube_dl.communicate()[0]
            errcode = update_youtube_dl.returncode
            #print(out)
            if len(err[1].strip()) !=0  or re.search("ERROR:", out):
                #print ("Standard error of youtube-dl:")
                #print (err[1])
                #print ("Using current version of youtube-dl ..")
                self.setStatus(State.YTDL_UPDATE_FAIL)
                self.updateAllViews()
            else:
                self.setStatus(State.YTDL_UPDATE_SUCCESS)
                self.updateAllViews()
            self.setStatus(old_status)
            self.updateAllViews()

    '''
        Functions That Facilitate Downloading
    '''

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

    def startDownloading(self):
        if self.validateOutputPath():
            if self.getStatus() == State.FILE_OPENED:
                self.setStatus(State.DOWNLOADING)
                self.error_log_file_name = "error_log_file_" + strftime("%Y-%m-%d_%H_%M_%S") + ".txt"
                self.downloadCurrentVideo()
                self.updateAllViews()
            elif self.getStatus() == State.DOWNLOADING:
                if self.currentVideoData()["Info"]["Status"] == videoState.DOWNLOADING:
                    self.clean_up_current_video(videoState.QUEUED)
                self.setStatus(State.FILE_OPENED)
                self.updateAllViews()

    def cleanUpRefrencesToThreads(self):
        #kill thread, clear queue, terminate process
        '''
        if(self.youtube_dl_output_timer != None): self.youtube_dl_output_timer.cancel()
        if(self.youtube_dl_thread != None): self.youtube_dl_thread.stop()
        if(self.youtube_dl_stdout_queue != None): self.youtube_dl_stdout_queue.clear()
        if(self.youtube_dl_stderr_queue != None): self.youtube_dl_stderr_queue.clear()
        '''
        if(self.youtube_dl_process != None): self.youtube_dl_process.terminate()
        #set them to null
        self.youtube_dl_thread = None
        self.youtube_dl_process = None
        self.youtube_dl_stdout_queue = None
        self.youtube_dl_stderr_queue = None
        self.youtube_dl_output_timer = None
        

    def downloadCurrentVideo(self):
        #if we are downloading for the first time, set all completed video sto queued so they can be retried
        if(self.getCurrentVideoID() == 0):
            for video in self.videos:
                if video["Info"]["Status"] == videoState.COMPLETE:
                    video["Info"]["Status"] = videoState.QUEUED
        if(self.getCurrentVideoID() == self.numberOfVideos()):
            self.finished_all_downloads()
        elif self.currentVideoData()["Info"]["Status"] in [videoState.SKIPPED, videoState.CANCELLED, videoState.ERROR]:
            #skip
            self.advance_current_video()
            self.downloadCurrentVideo()
        else:
            self.cleanUpRefrencesToThreads()
            current_video_info = self.currentVideoData()
            
            #set program name
            input_command = []
            input_command.extend(["youtube-dl"])
            
            #set format and quality
            if(self.getOutputFormat()==Format.FLV or self.getOutputFormat()==Format.MP4):
                if(self.getOutputQuality()==Quality.HIGH):
                    input_command.extend(["--max-quality"])
                elif(self.getOutputQuality()==Quality.NORMAL):
                    input_command.extend(["--format"])
                input_command.extend([Format.toString[self.getOutputFormat()].lower()])
            elif(self.getOutputFormat()==Format.MP3 or self.getOutputFormat()==Format.WAV):
                input_command.extend(["--extract-audio", "--audio-format", Format.toString[self.getOutputFormat()].lower()])
                if(self.getOutputQuality()==Quality.NORMAL):
                    input_command.extend(["--audio-quality", "5"])
                elif(self.getOutputQuality()==Quality.HIGH):
                    input_command.extend(["--audio-quality", "0"])
            
            #add flags and output path
            input_command.extend(["--verbose","--newline", "--continue", "--ignore-errors", "--no-overwrites", "--no-check-certificate", "-o"])
        
            #set output title
            if((self.getOutputTitleFormat() == titleFormat.USE_YOUTUBE_TITLE) or (current_video_info["Title"].find("Title Avaliable When Downloading") >= 0)):
                input_command.extend([self.getOutputPath() + "\\" + "%(title)s.%(ext)s"])
            elif(self.getOutputTitleFormat() == titleFormat.USE_BOOKMARK_TITLE):
                input_command.extend([self.getOutputPath() + "\\" + current_video_info["Title"] + ".%(ext)s"])
            
            #add the video url and a restrict filename tag
            input_command.extend(["http://" + current_video_info["Url"], "--restrict-filenames"])
            #print(input_command)
            #http://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python

            #open thread and get output
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.clean_up_current_video(videoState.DOWNLOADING) 
            self.youtube_dl_process = Popen(input_command, stdout=PIPE, stderr=PIPE, bufsize=1, close_fds=self.ON_POSIX, startupinfo=startupinfo)
            self.youtube_dl_stdout_queue = Queue()
            self.youtube_dl_stderr_queue = Queue()
            self.youtube_dl_thread = Thread(target=self.enqueue_output, args=(self.youtube_dl_process.stdout,
                                                                                     self.youtube_dl_process.stderr,
                                                                                     self.youtube_dl_stdout_queue,
                                                                                     self.youtube_dl_stderr_queue))
            self.youtube_dl_thread.daemon = True # thread dies with the program
            self.youtube_dl_thread.start()
            self.update_current_video_info_timer()
            self.updateAllViews()
            
    def finished_all_downloads(self):
        #this freezes program
        self.setCurrentVideoID(0)
        self.setStatus(State.COMPLETE)
        self.updateAllViews()
        self.setStatus(State.FILE_OPENED)
        self.updateAllViews()

    def error_list(self):
        #check if an error occured
        stderr = self.youtube_dl_stderr_queue
        lines = []
        while True:
            try:  line = stderr.get_nowait()
            except Empty:
                break
            else:
                #skip over [debug] lines which end up in stderr
                if line.startswith(b"[debug]") == False:
                    lines.append(line)
        #will be full of errors if they occured
        return lines
        
    def update_current_video_info_timer(self):
        if self.getStatus() == State.DOWNLOADING:
                lines = []
                #if line is empty are we still appending?
                while True:
                    try:  line = self.youtube_dl_stdout_queue.get_nowait()
                    except Empty:
                        #if the thread is alive
                        if(self.youtube_dl_process.poll() == None):
                            #warning, there could be a case where bewteen the try and this poll the dameon dies
                            #error occured during execution
                            error_list = self.error_list()
                            if(len(error_list) > 0):
                                self.log_error_to_file(error_list)
                                self.clean_up_current_video(videoState.ERROR)
                                self.advance_current_video()
                                self.downloadCurrentVideo()
                            elif self.currentVideoData()["Info"]["Status"] == videoState.CANCELLED:
                                self.advance_current_video()
                                self.downloadCurrentVideo()
                            else:
                                #continue
                                self.youtube_dl_output_timer = Timer(0.05, self.update_current_video_info_timer)
                                self.youtube_dl_output_timer.start()
                        #thread exited okay
                        elif(self.youtube_dl_process.poll() == 0):
                            #error occured after completion
                            error_list = self.error_list()
                            if(len(error_list) > 0):
                                self.log_error_to_file(error_list)
                                self.clean_up_current_video(videoState.ERROR)
                            #completed okay
                            elif self.currentVideoData()["Info"]["Status"] != videoState.CANCELLED:
                                self.clean_up_current_video(videoState.COMPLETE)
                            self.advance_current_video()
                            self.downloadCurrentVideo()
                        elif(self.youtube_dl_process.poll() == 1):
                            error_list = self.error_list()
                            if(len(error_list) > 0):
                                self.log_error_to_file(error_list)
                                self.clean_up_current_video(videoState.ERROR)
                            self.advance_current_video()
                            self.downloadCurrentVideo()
                        break
                    else:
                        #use regular expression to set video title, this is incase the video was not found in a bookmark
                        #and is missing it's title in the UI. If the title is not missing it will simply overwrite what it was
                        #originally, having no effect
                        download_filename = re.match(r"^\[download\] Destination: .*\\(.*)\..*$", line.decode("utf-8"))
                        if(download_filename != None):
                            self.currentVideoData()["Title"] = download_filename.group(1)
                        download_states = re.match(r"^\[download\]  (.*) of (.*) at\s{1,2}(.*) ETA (.*).*$", line.decode("utf-8"))
                        if(download_states != None):
                            self.currentVideoData()["Info"]["Percent"] = download_states.group(1)
                            self.currentVideoData()["Info"]["Size"] = download_states.group(2)
                            self.currentVideoData()["Info"]["Speed"] = download_states.group(3)
                            self.currentVideoData()["Info"]["remainingTime"] = download_states.group(4)
                            self.updateAllViews()
                        #append the line to the lines list
                        lines.append(line)
                #print lines to screen
                #for line in lines:
                    #print(str(line))
                

    #add stdout and stderr lines to queue
    def enqueue_output(self, out, err, queue_stdout, queue_stderr):
        for line in iter(out.readline, b''):
            queue_stdout.put(line)
        out.close()
        for line in iter(err.readline, b''):
            queue_stderr.put(line)
        err.close()

    '''
        Debugging and Error Logging Functions
    '''

    def log_error_to_file(self, error_list):
        #print("----------------")
        #for error in error_list:
        #    print(str(error))
        #print("----------------")
        #a flag to append
        file = open(self.error_log_file_name, 'a', encoding='utf8')
        file.write("----------------\n")
        file.write("Video ID: "+ str(self.getCurrentVideoID()))
        file.write("\n")
        file.write("Video Title: "+ self.currentVideoData()["Title"])
        file.write("\n")
        file.write("Video URL: "+ self.currentVideoData()["Url"])
        file.write("\n")
        file.write("Error: " + ''.join(str(error_list)))
        file.write("\n")
        file.write("----------------\n")
        file.close()

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
        print(self.currentVideoData())
        print("==================================")

    def say_clicked(self):
         print ("clicked!")
