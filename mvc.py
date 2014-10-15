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

class State:
    NO_OPEN_FILE = 0
    EMPTY_FILE = 1
    OPENING_FILE = 2
    FILE_OPENED = 3
    DOWNLOADING = 4
    UPDATING = 5
    YTDL_UPDATE_FAIL = 6
    YTDL_UPDATE_SUCCESS = 7

class Format:
    FLV = 0
    MP4 = 1
    MP3 = 2
    WAV = 3
    toString = {0: "Flv",
                1: "Mp4",
                2: "Mp3",
                3: "Wav"}

class Quality:
    NORMAL = 0
    HIGH = 1
    toString = {0: "Normal",
                1: "High"}

class titleFormat:
    USE_BOOKMARK_TITLE = 0
    USE_YOUTUBE_TITLE = 1
    toString = {0: "Use Bookmark Title",
                1: "Use Youtube Title"}

class videoState:
    QUEUED = 0
    SKIPPED = 1
    CANCELLED = 2
    CONVERTING = 3
    DOWNLOADING = 4
    toString = {0: "Queued",
                1: "Skip",
                2: "Cancelled",
                3: "Converting",
                4: "Downloading"}


class View(Frame):

    #Initialize widgets of interest that will have it's states altered at runtime.
    #The reason for doing this is because no widget is added dynamically. All are
    #   created only once during the initialization phase.
    menubar = None
    filemenu = None
    aboutmenu = None
    videoTree = None
    buttons = {"browse_button": None,
               "download_button": None}
    comboBoxes = {"format": None,
                  "quality": None,
                  "naming": None}
    entries = {"output_path": None}

    def enableOptions(self):
        self.buttons["browse_button"]['state'] = "normal"
        self.comboBoxes["format"]['state'] = "readonly"
        self.comboBoxes["quality"]['state'] = "readonly"
        self.comboBoxes["naming"]['state'] = "readonly"
        self.entries["output_path"]['state'] = "normal"
    def disableOptions(self):
        self.buttons["browse_button"]['state'] = "disabled"
        self.comboBoxes["format"]['state'] = "disabled"
        self.comboBoxes["quality"]['state'] = "disabled"
        self.comboBoxes["naming"]['state'] = "disabled"
        self.entries["output_path"]['state'] = "disabled"
    # File Menu Index
    # [0] = Open File
    # [1] = Update youtube-dl
    def enableOpenFile(self):
        self.filemenu.entryconfig(0,state="normal")
    def disableOpenFile(self):
        self.filemenu.entryconfig(0,state="disabled")
    def enableUpdate(self):
        self.filemenu.entryconfig(1,state="normal")
    def disableUpdate(self):
        self.filemenu.entryconfig(1,state="disabled")
    def enableDownload(self):
        self.buttons["download_button"]['state'] = "normal"
    def disableDownload(self):
        self.buttons["download_button"]['state'] = "disabled"

    def disableAllWidgets(self):
        self.disableOptions()
        self.disableOpenFile()
        self.disableUpdate()
        self.disableDownload()
    
    def __init__(self, master, model):
        #create window frame
        Frame.__init__(self, master)
        root.geometry("800x350")
        self.model = model
        self.iniWidgets()
	
    def iniWidgets(self):
        #create menu
        menubar = Menu(root)
        
        #add file menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.openFile, accelerator="Ctrl+O")
        filemenu.add_command(label="Update youtube-dl", command=self.model.updateYTDL, accelerator="Ctrl+U")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.destroy, accelerator="Alt+F4")
        menubar.add_cascade(label="File", menu=filemenu)

        #add help menu
        aboutmenu = Menu(menubar, tearoff=0)
        aboutmenu.add_command(label="About youtube-dl",
                              command=lambda: webbrowser.open_new_tab('http://rg3.github.io/youtube-dl/about.html'))
        aboutmenu.add_separator()
        aboutmenu.add_command(label="About eyb-dl", command=self.aboutEybDl, accelerator="F1")
        menubar.add_cascade(label="About", menu=aboutmenu)

        #display menu
        root.bind('<Control-O>', lambda x: self.openFile())
        root.bind('<Control-U>', lambda x: self.model.updateYTDL())
        root.bind('<Control-o>', lambda x: self.openFile())
        root.bind('<Control-u>', lambda x: self.model.updateYTDL())
        root.bind('<F1>', lambda x: self.aboutEybDl())
        root.config(menu=menubar)

        #create video table frame
        middleFrame = Frame(root)
        
        #create tree view(the video table)
        videoTree = ttk.Treeview(middleFrame, selectmode='browse')
        videoTree['show'] = 'headings'
        videoTree['columns'] = ('id', 'name', 'url', 'status')
        videoTree.column('id', anchor='w', width=50, stretch='false', minwidth=50)
        videoTree.heading('id', text='')
        videoTree.column('name', anchor='w', width=300, stretch='true', minwidth=100)
        videoTree.heading('name', text='Video Name')
        videoTree.column('url', anchor='w', width=200, stretch='true', minwidth=100)
        videoTree.heading('url', text='URL')
        videoTree.column('status', anchor='center', stretch='false', minwidth=50)
        videoTree.heading('status', text='Status')
        scroll = ttk.Scrollbar(middleFrame, orient= VERTICAL, command = videoTree.yview)
        scroll.pack(side=RIGHT, fill=Y)
        videoTree['yscroll'] = scroll.set
        videoTree.configure(yscrollcommand=scroll.set)
        videoTree.bind("<Button-3>", self.rightClickVideo)
        videoTree.bind("<Double-1>", self.doubleClickVideo)
        videoTree.pack(expand=YES, fill=BOTH)

        #display video table
        middleFrame.pack(side=TOP, fill=BOTH, expand=YES)

        #create bottom frame for options, status of the current video and download button
        bottomFrame = Frame(root, bg=root.cget('bg'))
        downloadButtonFrame = Frame(bottomFrame, relief=GROOVE, borderwidth=1)
        optionsChoicesFrame = Frame(bottomFrame, relief=GROOVE, borderwidth=1)
        statusFrame = Frame(bottomFrame, relief=GROOVE, borderwidth=1,  bg=root.cget('bg'))

        #make frames use grid layout
        optionsChoicesFrame.grid()
        statusFrame.grid()

        #setup labels for options
        Label(optionsChoicesFrame, text="Options").grid(row=0, column=1, sticky=W)
        Label(optionsChoicesFrame, text="Format:").grid(row=1, column=1, sticky=W)
        Label(optionsChoicesFrame, text="Quality:").grid(row=2, column=1, sticky=W)
        Label(optionsChoicesFrame, text="Naming:").grid(row=3, column=1, sticky=W)
        Label(optionsChoicesFrame, text="Output:").grid(row=4, column=1, sticky=W)

        #create the comboboxes for options
        formatBox = ttk.Combobox(optionsChoicesFrame, state='readonly')
        qualityBox = ttk.Combobox(optionsChoicesFrame, state='readonly')
        fileNameBox = ttk.Combobox(optionsChoicesFrame, state='readonly')

        #fill in comboboxes using weird hack because formatBox["values"] is a weird list
        # and won't do listOfFormats = Format.toString.values() (bad string casting)
        listOfFormats = []
        for formatStr in Format.toString.values():
            listOfFormats.append(formatStr)
        formatBox["values"] = listOfFormats
        
        listOfQualities = []
        for qualityStr in Quality.toString.values():
            listOfQualities.append(qualityStr)
        qualityBox["values"] = listOfQualities

        listOfTitleFormats = []
        for titleFormatStr in titleFormat.toString.values():
            listOfTitleFormats.append(titleFormatStr)
        fileNameBox['values']= listOfTitleFormats
        
        #add listeners for when an option is selected
        formatBox.bind("<<ComboboxSelected>>", self.say_clicked())
        qualityBox.bind("<<ComboboxSelected>>", self.say_clicked())
        fileNameBox.bind("<<ComboboxSelected>>", self.say_clicked())

        #setup what is selected in the combobox
        formatBox.current(self.model.getOutputFormat())
        qualityBox.current(self.model.getOutputQuality())
        fileNameBox.current(self.model.getOutputTitleFormat())

        #create output folder entry
        outputFolder = Entry(optionsChoicesFrame, width=40)
        outputFolder.insert(0, self.model.getOutputPath())
        outputFolder.xview('moveto', 1)

        #create browse button
        browseButton = Button(optionsChoicesFrame, width=10, text="Browse")
                
        #add all input options to the grid
        formatBox.grid(row=1, column=2, sticky=W)
        qualityBox.grid(row=2, column=2, sticky=W)
        fileNameBox.grid(row=3, column=2, sticky=W)
        outputFolder.grid(row=4, column=2, sticky=W) 
        browseButton.grid(row=4, column=3, sticky=W)
        
        #add current video status labels        
        Label(statusFrame, text="Video ID:").grid(row=0, column=1, sticky=W)
        Label(statusFrame, text="Percent Done:").grid(row=1, column=1, sticky=W)
        Label(statusFrame, text="Current Status:").grid(row=2, column=1, sticky=W)
        Label(statusFrame, text="Speed [kb/s]:").grid(row=3, column=1, sticky=W)
        Label(statusFrame, text="Time Remaining:").grid(row=4, column=1, sticky=W)

        #add current video statuses
        Label(statusFrame, text="N/A").grid(row=0, column=2, sticky=W)
        Label(statusFrame, text="N/A").grid(row=1, column=2, sticky=W)
        Label(statusFrame, text="N/A").grid(row=2, column=2, sticky=W)
        Label(statusFrame, text="N/A").grid(row=3, column=2, sticky=W)
        Label(statusFrame, text="N/A").grid(row=4, column=2, sticky=W)

        #add download button
        download = Button(downloadButtonFrame, text="Begin Download", command=self.model.startDownloading)
        download.pack(fill=BOTH, expand=YES, anchor=CENTER)

        #add all frames to screen
        optionsChoicesFrame.pack(side=LEFT, fill=Y)
        statusFrame.pack(side=LEFT, after=optionsChoicesFrame, fill=BOTH, expand=YES)
        downloadButtonFrame.pack(side=BOTTOM, expand=YES, anchor=SE, fill=Y)
        bottomFrame.pack(side=BOTTOM, fill=BOTH)

        #set outer class variables so that widgets can be accessed by other methods
        self.menubar = menubar
        self.filemenu = filemenu
        self.aboutmenu = aboutmenu
        self.videoTree = videoTree
        self.buttons["browse_button"] = browseButton
        self.buttons["download_button"] = download
        self.comboBoxes["format"] = formatBox
        self.comboBoxes["quality"] = qualityBox
        self.comboBoxes["naming"] = fileNameBox
        self.entries["output_path"] = outputFolder
	
        

    def say_clicked(self):
         print ("clicked!")

    def doubleClickVideo(self, event):
        if(self.videoTree.selection() != ""):
            item = self.videoTree.selection()[0]
            webbrowser.open_new_tab(self.videoTree.item(item,"values")[2])

    def rightClickVideo(self, event):
        if(self.videoTree.selection() != ""):
            item = self.videoTree.selection()[0]
            print(self.videoTree.item(item,"values"))
            menu = Menu(root, tearoff=0)
            menu.add_command(label="Open Video",
                             command= lambda : webbrowser.open_new_tab(self.videoTree.item(item,"values")[2]))
            if (self.videoTree.item(item,"values")[3] == "Queued"):
                menu.add_command(label="Skip Selected",
                                 command= lambda : self.model.removeItemFromList(self.videoTree.item(item,"values")[0]))
            elif (self.videoTree.item(item,"values")[3] == "Skip"):
                menu.add_command(label="Queue Selected",
                                 command= lambda : self.model.queueItemFromList(self.videoTree.item(item,"values")[0]))
            elif (self.videoTree.item(item,"values")[3] == "Converting"):
                menu.add_command(label="Cancel Selected",
                                 command= lambda : self.model.queueItemFromList(self.videoTree.item(item,"values")[0]))
            elif (self.videoTree.item(item,"values")[3] == "Downloading"):
                menu.add_command(label="Cancel Selected",
                                 command= lambda : self.model.queueItemFromList(self.videoTree.item(item,"values")[0]))
            #no case for cancelled, there is no current easy way to requeue a cancelled download.
            menu.post(event.x_root, event.y_root)
		
    def openFile(self):
        filepath = filedialog.askopenfilename()
        self.model.loadBookmark(filepath)

    def updateVideoTable(self):
        for item in self.videoTree.get_children():
            self.videoTree.delete(item)
        id = 0
        for video in self.model.videos:
            self.videoTree.insert('',
                                  'end',
                                  text='',
                                  values=(id,
                                          video["Title"],
                                          video["Url"],
                                          videoState.toString[video["Info"]["Status"]]
                                          )
                                  )
            id += 1

    def update(self):
        print(self.model.program_status)
        print("self.updateVideoTable()")
        #Update video table right away
        self.updateVideoTable()
        #Assume nothing can be used. Enable widgets that are relevent
        self.disableAllWidgets()
        #Any states needing a messagebox don't are always reverted to the previous state
        #   by the model. This is so that the view can temporarily see an error occured
        if self.model.getStatus() == State.NO_OPEN_FILE:		
            self.enableOpenFile()
            self.enableUpdate()
        elif self.model.getStatus() == State.EMPTY_FILE:
            tkinter.messagebox.showerror(
            "Open file",
            "Videos were not read from file.")
        elif self.model.getStatus() == State.OPENING_FILE:
            pass
        elif self.model.getStatus() == State.FILE_OPENED:
            self.enableOptions()		
            self.enableOpenFile()
            self.enableUpdate()
            self.enableDownload()
        elif self.model.getStatus() == State.DOWNLOADING:
            self.enableDownload()
            #set downloading button text to say pause
        elif self.model.model.getStatus() == State.UPDATING:
            pass
        elif self.model.getStatus() == State.YTDL_UPDATE_FAIL:
            tkinter.messagebox.showerror(
            "Failed To Update",
            "Could not update update youtube-dl.")
        elif self.model.getStatus() == State.YTDL_UPDATE_SUCCESS:
            tkinter.messagebox.showinfo(
            "YouTube-DL",
            "The newest version of youtube-dl will now be used.")
        
		
    def aboutEybDl(self):
        #setup toplevel
        aboutYTDL = Toplevel(root)
        aboutYTDL.geometry("270x200")
        aboutYTDL.transient(root)
        aboutYTDL.grab_set()
        aboutYTDL.title("About eyb-dl")
        aboutYTDL.resizable(FALSE,FALSE)
        
        #add strings
        about_heading = "Easy Youtube Bookmark Downloader"
        about_body = "The easiest way to batch archieve videos. "
        about_body += "Originally developed as an interactive terminal program. "
        about_body += "Dedicated to Kathan Desai and Harsh Oza."
        about_version = "Version 3.0 [24/09/14]"
        author_text = "Author: Satbir Saini (satbir.kira@gmail.com)"
        author_website = "satbirkira.com"

        #create frame
        bottomFrame = Frame(aboutYTDL)

        #add widgets
        heading = Label(aboutYTDL, text=about_heading, font="Helvetica", foreground="Red") 
        body = Message(aboutYTDL, text=about_body, anchor=W, width=270)
        version = Label(aboutYTDL, text=about_version, anchor=W)
        author = Label(aboutYTDL, text=author_text, anchor=W)
        website = Label(aboutYTDL, text=author_website, anchor=W, foreground="Blue")
        close = Button(bottomFrame, text="Close", command=aboutYTDL.destroy)
        
        #pack widgets
        heading.pack(side=TOP, fill=X)
        body.pack(side=TOP, fill=X, after=heading)
        version.pack(side=BOTTOM, fill=X)
        author.pack(side=BOTTOM, fill=X, before=version)
        website.pack(side=BOTTOM, fill=X, before=author)
        close.pack(side=RIGHT, padx=5, pady=5)
        bottomFrame.pack(side=BOTTOM, before=website, fill=X)

        #bind accelerator
        website.bind("<Button-1>", lambda x: webbrowser.open_new_tab('http://satbirkira.com'))

#===
#===	

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
        #get bookmark filepath
        self.setFilePath(filepath)
        try:
            check_file = open(self.getFilePath())
            print ("File opened successfully.")
            check_file.close()
        except:
            self.setStatus(State.EMPTY_FILE)
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
            else:
                self.setStatus(State.FILE_OPENED)
            print ("here")
        self.updateAllViews()
        print ("here")
    
    def updateYTDL(self):
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
        if err[1].strip() or re.search("ERROR:", out):
            print ("Standard error of youtube-dl:")
            print (err[1])
            print ("Using current version of youtube-dl ..")
            self.setStatus(State.YTDL_UPDATE_SUCCESS)
        else:
            self.setStatus(State.YTDL_UPDATE_FAIL)
        self.updateAllViews()
        self.setStatus(old_status)
        

    def startDownloading(self):
        print (self.filepath)
        self.updateAllViews()
    #http://stackoverflow.com/questions/2082850/real-time-subprocess-popen-via-stdout-and-pipe

    def pauseDownloading(self):
        print (self.filepath)
        self.updateAllViews()

    def videoStatus(self, i):
        return self.videos[i]["Info"]["Status"]

    def changeVideoStatus(self, i, status):
        self.videos[i]["Info"]["Status"] = status
        
    def cancelVideo(self):
        return None

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


# Initial Window Widget
root = Tk()
root.title("Easy Youtube Bookmark Downloader 3.0")
root.minsize(700,350)
# Open View
mainModel = Model()
mainView = View(root, mainModel)
mainModel.addView(mainView)
# Enter GUI Event Loop
root.mainloop()
