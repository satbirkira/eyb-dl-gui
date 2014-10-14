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

class state:
    NO_OPEN_FILE = 0
    EMPTY_FILE = 1
    OPENING_FILE = 2
    FILE_OPENED = 3
    DOWNLOADING = 4
    UPDATING = 5
    YTDL_UPDATE_FAIL =6
    YTDL_UPDATE_SUCCESS =7

class quality:
    FLV = 0
    MP4 = 1
    MP3 = 2
    WAV = 3

class format:
    NORMAL = 0
    HIGH = 1

class videoState:
    QUEUED = 0
    SKIPPED = 1
    CANCELED = 2
    CONVERTING = 3
    


class View(Frame):

    menubar = None
    videoTree = None
    options = None
    videoStatus = None
    
    def __init__(self, master, model):
        #create window frame
        Frame.__init__(self, master)
        root.geometry("800x350")
        self.model = model
        self.iniWidgets()
	
    def iniWidgets(self):
        #create menu
        self.menubar = Menu(root)
        
        #add file menu
        filemenu = Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.openFile, accelerator="Ctrl+O")
        filemenu.add_command(label="Update youtube-dl", command=self.model.updateYTDL, accelerator="Ctrl+U")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.destroy, accelerator="Alt+F4")
        self.menubar.add_cascade(label="File", menu=filemenu)

        #add help menu
        aboutmenu = Menu(self.menubar, tearoff=0)
        aboutmenu.add_command(label="About youtube-dl", command=lambda: webbrowser.open_new_tab('http://rg3.github.io/youtube-dl/about.html'))
        aboutmenu.add_separator()
        aboutmenu.add_command(label="About eyb-dl", command=self.aboutEybDl, accelerator="F1")
        self.menubar.add_cascade(label="About", menu=aboutmenu)

        #display menu
        root.bind('<Control-O>', lambda x: self.openFile())
        root.bind('<Control-U>', lambda x: self.model.updateYTDL())
        root.bind('<Control-o>', lambda x: self.openFile())
        root.bind('<Control-u>', lambda x: self.model.updateYTDL())
        root.bind('<F1>', lambda x: self.aboutEybDl())
        root.config(menu=self.menubar)

        #create video table frame
        middleFrame = Frame(root)
        
        #create tree view(the video table)
        self.videoTree = ttk.Treeview(middleFrame, selectmode='browse')
        self.videoTree['show'] = 'headings'
        self.videoTree['columns'] = ('id', 'name', 'url', 'status')
        self.videoTree.column('id', anchor='w', width=50, stretch='false', minwidth=50)
        self.videoTree.heading('id', text='')
        self.videoTree.column('name', anchor='w', width=300, stretch='true', minwidth=100)
        self.videoTree.heading('name', text='Video Name')
        self.videoTree.column('url', anchor='w', width=200, stretch='true', minwidth=100)
        self.videoTree.heading('url', text='URL')
        self.videoTree.column('status', anchor='center', stretch='false', minwidth=50)
        self.videoTree.heading('status', text='Status')
        scroll = ttk.Scrollbar(middleFrame, orient= VERTICAL, command = self.videoTree.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.videoTree['yscroll'] = scroll.set
        self.videoTree.configure(yscrollcommand=scroll.set)
        self.videoTree.bind("<Button-3>", self.rightClickVideo)
        self.videoTree.bind("<Double-1>", self.doubleClickVideo)
        self.videoTree.pack(expand=YES, fill=BOTH)

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
        formatBox['values']=('Flv', 'Mp4', 'Mp3', 'Wav')
        qualityBox['values']=('Normal', 'High')
        fileNameBox['values']=('Use Bookmark Title', 'Use Youtube Title')
        formatBox.bind("<<ComboboxSelected>>", self.say_clicked())
        qualityBox.bind("<<ComboboxSelected>>", self.say_clicked())
        fileNameBox.bind("<<ComboboxSelected>>", self.say_clicked())

        #default HQ Flv
        formatBox.current(0)
        qualityBox.current(0)
        fileNameBox.current(0)

        #create output folder entry
        outputFolder = Entry(optionsChoicesFrame, width=40)
        outputFolder.insert(0, os.getcwd())
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
        Label(statusFrame, text="Video Name:").grid(row=1, column=1, sticky=W)
        Label(statusFrame, text="Current Status:").grid(row=2, column=1, sticky=W)
        Label(statusFrame, text="Speed [mb/s]:").grid(row=3, column=1, sticky=W)
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

        #set outer class variables so that widgets can be accessed by methods
        self.options = optionsChoicesFrame


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
            if (self.videoTree.item(item,"values")[3] == "Queued"):
                print(self.videoTree.item(item,"values")[3])
                menu = Menu(root, tearoff=0)
                menu.add_command(label="Open Video", command= lambda : webbrowser.open_new_tab(self.videoTree.item(item,"values")[2]))
                menu.add_command(label="Skip Selected", command= lambda : self.model.removeItemFromList(self.videoTree.item(item,"values")[0]))
                menu.post(event.x_root, event.y_root)
            elif (self.videoTree.item(item,"values")[3] == "Skip"):
                print(self.videoTree.item(item,"values")[3])
                menu = Menu(root, tearoff=0)
                menu.add_command(label="Open Video", command= lambda : webbrowser.open_new_tab(self.videoTree.item(item,"values")[2]))
                menu.add_command(label="Queue Selected", command= lambda : self.model.queueItemFromList(self.videoTree.item(item,"values")[0]))
                menu.post(event.x_root, event.y_root)
            elif (self.videoTree.item(item,"values")[3] == "Converting"):
                print("Converting")
            elif (re.search(self.videoTree.item(item,"values")[3], "Downloading")):
                print("Downloading")
		
    def openFile(self):
        filepath = filedialog.askopenfilename()
        self.model.loadBookmark(filepath)

    def updateVideoTable(self):
        for item in self.videoTree.get_children():
            self.videoTree.delete(item)
        id = 0
        for video in self.model.videos:
            self.videoTree.insert('', 'end', text='', values=(id, video[1], video[0], video[2]))
            id += 1

    def update(self):
        print ("here3")
        print(self.model.program_status)
        print("Updating View")
        self.updateVideoTable()
        #on error dialogs, attach command to pressing okay to restore old state
        if self.model.program_status == 1:
            tkinter.messagebox.showerror(
            "Open file",
            "Videos were not read from file.")
        elif self.model.program_status == 3:
            print("Files Opened, Updaing Video Table")
            self.updateVideoTable()
        elif self.model.program_status == 6:
            print("Updating")
        elif self.model.program_status == 7:
            tkinter.messagebox.showerror(
            "Failed To Update",
            "Could not update update youtube-dl.")
        elif self.model.program_status == 8:
            tkinter.messagebox.showinfo(
            "YouTube-DL",
            "The newest version of youtube-dl will now be used.")
        elif self.model.program_status == 4:
            #disable download options
            for child in self.options.winfo_children():
                child['state']="disabled"
		
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
        about_body = """The easiest way to batch archieve videos.
Originally developed as an interactive terminal program. Dedicated to Kathan Desai and Harsh Oza.
        """
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

    filepath = ""
    outputPath = ""
    videos=[]	
    views =[]
    program_status = state.NO_OPEN_FILE

    #default HQ FLV
    outputFormat = 0
    outputQuality = 1

    #video downloading info
    current_video = 0

    #put this in the array of videos
    youtube_title = ""
    current_status = None
    current_speed = 0
    time_remaning = 0
    

    def __init__(self):
        self.outputPath = os.getcwd()
        self.changeStatus(state.NO_OPEN_FILE)
        
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

    def changeStatus(self, status):
        self.program_status = status

    def getStatus(self):
        return self.program_status  
        

    def loadBookmark(self, filepath):
        self.filepath = filepath
        try:
            check_file = open(self.filepath)
            print ("File opened successfully.")
            check_file.close()
        except:
            changeStatus(state.EMPTY_FILE)
        else:
            #load the bookmark using regex
            changeStatus(state.OPENING_FILE)
            content_file = codecs.open(self.filepath, 'r', 'utf-8')
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
                formated_video = ["www.youtube.com/watch?v=" + video[0], formated_title, "Queued"]
                if formated_video[0] not in newlist_urls:
                        newlist_urls.append(formated_video[0])
                        newlist.append(formated_video)
            #store fixed video list
            self.videos = newlist
            if self.numberOfVideos() == 0:
                changeStatus(state.EMPTY_FILE)
            else:
                changeStatus(state.FILE_OPENED)
            print ("here")
        self.updateAllViews()
        print ("here")
    
    def updateYTDL(self):
        print(os.getcwd()+"\youtube-dl.exe --update")
        old_status = self.getStatus()
        self.changeStatus(state.UPDATING)
        self.updateAllViews()
        update_youtube_dl = subprocess.Popen(os.getcwd()+"\youtube-dl.exe --update", stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
        err = update_youtube_dl.communicate()
        out = update_youtube_dl.communicate()[0]
        errcode = update_youtube_dl.returncode
        print(out)
        if err[1].strip() or re.search("ERROR:", out):
            print ("Standard error of youtube-dl:")
            print (err[1])
            print ("Using current version of youtube-dl ..")
            self.changeStatus(state.YTDL_UPDATE_SUCCESS)
        else:
            self.changeStatus(state.YTDL_UPDATE_FAIL)
        self.updateAllViews()
        self.changeStatus(old_status)
        

    def startDownloading(self):
        print (self.filepath)
        self.updateAllViews()
    #http://stackoverflow.com/questions/2082850/real-time-subprocess-popen-via-stdout-and-pipe

    def pauseDownloading(self):
        print (self.filepath)
        self.updateAllViews()

    def videoStatus(self, i):
        return self.videos[i][2]

    def changeVideoStatus(self, i, status):
        self.videos[i][2] = status

    def currentVideoStatus(self):
        i = self.current_video
        return self.videos[i][2]

    def cancelVideo(self):
        return None

    def numberOfVideos(self):
        return len(self.videos)

    def removeItemFromList(self, i):
        i = int(i)
        if self.videoStatus(i) == "Queued":
            self.changeVideoStatus(i, "Skip")
            self.updateAllViews() #for some reason, this must be repeated at every condition
        elif re.search("Downloading", self.videoStatus(i)) or re.search("Converting", self.videoStatus(i)):
            self.cancelVideo()
            self.changeVideoStatus(i, "Cancelled")
            self.updateAllViews()
        
    def queueItemFromList(self, i):
        i = int(i)
        if self.videoStatus(i) == "Skip":
            self.changeVideoStatus(i, "Queued")
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
