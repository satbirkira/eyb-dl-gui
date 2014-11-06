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



class View(Frame):

    #Initialize widgets of interest that will have it's states altered at runtime.
    #The reason for doing this is because no widget is added dynamically. All are
    #   created only once during the initialization phase.
    root = None
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
    labels = {"video_id": None,
              "percent_done": None,
              "size":None,
              "speed":None,
              "time_remaning":None}

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
        
    def updateDownloadButtonText(self):
        if self.model.getStatus() == State.DOWNLOADING:
            self.buttons["download_button"]['text'] = "Pause Download"
        else:
            self.buttons["download_button"]['text'] = "Begin Download"
    
    def disableAllWidgets(self):
        self.disableOptions()
        self.disableOpenFile()
        self.disableUpdate()
        self.disableDownload()

    def clearLabels(self):
        self.labels["video_id"]['text'] = "N/A"
        self.labels["percent_done"]['text'] = "N/A"
        self.labels["size"]['text'] = "N/A"
        self.labels["speed"]['text'] = "N/A"
        self.labels["time_remaning"]['text'] = "N/A"
    
    def __init__(self, root, model):
        #create window frame
        root.title("Unofficial Youtube-dl GUI 3.0 -- By Satbir Saini")
        root.minsize(700,350)
        self.root = root
        Frame.__init__(self, self.root)
        self.root.geometry("800x350")
        self.model = model
        self.iniWidgets()
	
    def iniWidgets(self):
        #create menu
        menubar = Menu(self.root)
        
        #add file menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.openFile, accelerator="Ctrl+O")
        filemenu.add_command(label="Update youtube-dl", command=self.model.updateYTDL, accelerator="Ctrl+U")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.destroy, accelerator="Alt+F4")
        menubar.add_cascade(label="File", menu=filemenu)

        #add help menu
        aboutmenu = Menu(menubar, tearoff=0)
        aboutmenu.add_command(label="About youtube-dl",
                              command=lambda: webbrowser.open_new_tab('http://rg3.github.io/youtube-dl/about.html'))
        aboutmenu.add_separator()
        aboutmenu.add_command(label="About eyb-dl", command=self.aboutEybDl, accelerator="F1")
        menubar.add_cascade(label="About", menu=aboutmenu)

        #display menu
        self.root.bind('<Control-O>', lambda x: self.openFile())
        self.root.bind('<Control-U>', lambda x: self.model.updateYTDL())
        self.root.bind('<Control-o>', lambda x: self.openFile())
        self.root.bind('<Control-u>', lambda x: self.model.updateYTDL())
        self.root.bind('<F1>', lambda x: self.aboutEybDl())
        self.root.config(menu=menubar)

        #create video table frame
        middleFrame = Frame(self.root)
        
        #create tree view(the video table)
        videoTree = ttk.Treeview(middleFrame, selectmode='extended')#selectmode='browse'
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
        bottomFrame = Frame(self.root, bg=self.root.cget('bg'))
        downloadButtonFrame = Frame(bottomFrame, relief=GROOVE, borderwidth=1)
        optionsChoicesFrame = Frame(bottomFrame, relief=GROOVE, borderwidth=1)
        statusFrame = Frame(bottomFrame, relief=GROOVE, borderwidth=1,  bg=self.root.cget('bg'))

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
        
        #setup what is selected in the combobox
        formatBox.current(self.model.getOutputFormat())
        qualityBox.current(self.model.getOutputQuality())
        fileNameBox.current(self.model.getOutputTitleFormat())

        #add listeners for combobozes
        formatBox.bind("<<ComboboxSelected>>", lambda x: self.model.setOutputFormat(formatBox['values'].index(formatBox.get())))
        qualityBox.bind("<<ComboboxSelected>>", lambda x: self.model.setOutputQuality(qualityBox['values'].index(qualityBox.get())))
        fileNameBox.bind("<<ComboboxSelected>>", lambda x: self.model.setOutputTitleFormat(fileNameBox['values'].index(fileNameBox.get())))

        #create output folder entry
        sv = StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: self.model.setOutputPath(sv.get()))
        outputFolder = Entry(optionsChoicesFrame, width=40, textvariable=sv)
        outputFolder.insert(0, self.model.getOutputPath())
        outputFolder.xview('moveto', 1)

        #create browse button
        browseButton = Button(optionsChoicesFrame, width=10, text="Browse", command=self.browseOutputPath)
                
        #add all input options to the grid
        formatBox.grid(row=1, column=2, sticky=W)
        qualityBox.grid(row=2, column=2, sticky=W)
        fileNameBox.grid(row=3, column=2, sticky=W)
        outputFolder.grid(row=4, column=2, sticky=W) 
        browseButton.grid(row=4, column=3, sticky=W)
        
        #add current video status labels        
        Label(statusFrame, text="Video ID:").grid(row=0, column=1, sticky=W)
        Label(statusFrame, text="Percent Done:").grid(row=1, column=1, sticky=W)
        Label(statusFrame, text="Video Size:").grid(row=2, column=1, sticky=W)
        Label(statusFrame, text="Download Speed:").grid(row=3, column=1, sticky=W)
        Label(statusFrame, text="Time Remaining:").grid(row=4, column=1, sticky=W)

        #add current video statuses
        video_id_label = Label(statusFrame, text="")
        percent_label = Label(statusFrame, text="")
        size_label = Label(statusFrame, text="")
        speed_label = Label(statusFrame, text="")
        time_remaning_label = Label(statusFrame, text="")
        
        video_id_label.grid(row=0, column=2, sticky=W)
        percent_label.grid(row=1, column=2, sticky=W)
        size_label.grid(row=2, column=2, sticky=W)
        speed_label.grid(row=3, column=2, sticky=W)
        time_remaning_label.grid(row=4, column=2, sticky=W)

        #add download button
        download = Button(downloadButtonFrame, text="N/A", command=self.model.startDownloading)
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
        self.labels["video_id"] = video_id_label
        self.labels["percent_done"] = percent_label
        self.labels["size"] = size_label
        self.labels["speed"] = speed_label
        self.labels["time_remaning"] = time_remaning_label
        self.clearLabels()

    def browseOutputPath(self):
        folderpath = filedialog.askdirectory()
        #no need to tell model here, the StringVar has already been setup to do so
        if(len(folderpath) != 0):
            self.entries["output_path"].delete(0, len(self.entries["output_path"].get()))
            self.entries["output_path"].insert(0, folderpath)
            self.entries["output_path"].xview('moveto', 1)
	        

    def say_clicked(self):
         print ("clicked!")

    def doubleClickVideo(self, event):
        if(self.videoTree.selection() != ""):
            item = self.videoTree.selection()[0]
            webbrowser.open_new_tab(self.videoTree.item(item,"values")[2])

    def rightClickVideo(self, event):
        if(len(self.videoTree.selection()) != 0):
            print(len(self.videoTree.selection()))
            #put context menu over the item that was right clicked
            item = self.videoTree.identify('item', event.x,event.y)
            print(self.videoTree.item(item,"values"))
            menu = Menu(self.root, tearoff=0)

            def queueSelection():
                indices = []
                #first get indices since references to the videos become invalid after
                #queueItemFromList() is called. This is due to emptying the videotree
                #and refilling on updating the view
                for item in self.videoTree.selection():
                    indices.append(self.videoTree.item(item,"values")[0])
                for index in indices:
                    self.model.queueItemFromList(index)
            def removeSelection():
                indices = []
                for item in self.videoTree.selection():
                    indices.append(self.videoTree.item(item,"values")[0])
                for index in indices:
                    self.model.removeItemFromList(index)

            def openSelection():
                for item in self.videoTree.selection():
                    webbrowser.open_new_tab(self.videoTree.item(item,"values")[2])
            
            menu.add_command(label="Open Video",
                             command= lambda : openSelection())
            if (self.videoTree.item(item,"values")[3] == "Queued"):
                menu.add_command(label="Skip Selected",
                                 command= lambda : removeSelection())
            elif (self.videoTree.item(item,"values")[3] == "Skip"):
                menu.add_command(label="Queue Selected",
                                 command= lambda : queueSelection())
            elif (self.videoTree.item(item,"values")[3] == "Downloading"):
                menu.add_command(label="Cancel Selected",
                                 command= lambda : removeSelection())
            #no case for cancelled, there is no current easy way to requeue a cancelled download.
            menu.post(event.x_root, event.y_root)
		
    def openFile(self):
        if self.model.getStatus() not in [State.DOWNLOADING, State.OPENING_FILE, State.UPDATING]:
            filepath = tkinter.filedialog.askopenfilename()
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
        #Update video table and download button text right away
        self.updateVideoTable()
        self.updateDownloadButtonText()
        #Assume nothing can be used. Enable widgets that are relevent
        self.disableAllWidgets()
        self.clearLabels()
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
            self.labels["video_id"]['text'] = str(self.model.getCurrentVideoID())
            self.labels["percent_done"]['text'] = self.model.currentVideoInformation()["Info"]["Percent"]
            self.labels["size"]['text'] = self.model.currentVideoInformation()["Info"]["Size"]
            self.labels["speed"]['text'] = self.model.currentVideoInformation()["Info"]["Speed"]
            self.labels["time_remaning"]['text'] = self.model.currentVideoInformation()["Info"]["remainingTime"]
        elif self.model.getStatus() == State.UPDATING:
            pass
        elif self.model.getStatus() == State.YTDL_UPDATE_FAIL:
            tkinter.messagebox.showerror(
            "Failed To Update",
            "Could not update update youtube-dl.")
        elif self.model.getStatus() == State.YTDL_UPDATE_SUCCESS:
            tkinter.messagebox.showinfo(
            "YouTube-DL",
            "The newest version of youtube-dl will now be used.")
        elif self.model.getStatus() == State.INVALID_OUTPUT_PATH:
            tkinter.messagebox.showerror(
            "Invalid Output Path",
            "The output directory is invalid.")
        elif self.model.getStatus() == State.COMPLETE:
            '''
            This has to be run in the main thread.
            Since we call downloadCurrentVideo() and eventaully finished_all_downloads() which updates the view
            This call freezes since tkinter is not thread safe. It's more of a headache to work around the issue.
            tkinter.messagebox.showerror(
            "Complete Automation",
            "The task has completed.")
            '''
        #update options widgets
        self.comboBoxes["format"].current(self.model.getOutputFormat())
        self.comboBoxes["quality"].current(self.model.getOutputQuality())
        self.comboBoxes["naming"].current(self.model.getOutputTitleFormat())
        
		
    def aboutEybDl(self):
        #setup toplevel
        aboutYTDL = Toplevel(self.root)
        aboutYTDL.geometry("270x200")
        aboutYTDL.transient(self.root)
        aboutYTDL.grab_set()
        aboutYTDL.title("About eyb-dl")
        aboutYTDL.resizable(FALSE,FALSE)
        
        #add strings
        about_heading = "Unofficial Youtube-dl GUI"
        about_body = "The easiest way to batch archieve videos. "
        about_body += "Originally developed as an interactive terminal program. "
        about_body += "Dedicated to Kathan Desai and Harsh Oza. And /g/"
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
