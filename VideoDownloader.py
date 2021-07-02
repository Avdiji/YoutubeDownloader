import os
import urllib.error
from tkinter import filedialog, StringVar, Tk, Label, Button, Entry, OptionMenu, Frame, HORIZONTAL
from tkinter.ttk import Progressbar
from pytube import YouTube
from os import path
from pytube.exceptions import RegexMatchError, VideoUnavailable
import threading

# X/Y position of frame children
CHILDREN_X = 65;
CHILDREN_Y = 100;

# Layout n stuff
ENTRY_WIDTH = 43
ENTRY_FONT = 'arial 13'
LABEL_FONT = 'arial 12'
BUTTON_COLOR = 'azure'
FRAME_COLOR = 'cyan'
ROOT_COLOR = 'lightblue'

# OUTPUT MESSAGES
MISSING_SOURCE = 'You must insert a valid Youtube-URL                    '
MISSING_PATH = 'You must insert a valid destination path                    '
INVALID_SOURCE = 'The given Youtube-URL was not found, please try again                    '
INVALID_PATH = 'The given destination path was not found                    '
DOWNLOAD_SUCCESSFUL = 'Video downloaded successfully                    '

# self explanatory?
OptionList = [
    ".mp4",
    ".mp3"
]


# needed to seperate gui from the actual download to prevent the gui from stuttering
class DownloadThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("starting download")
        Downloader()


# initialize the window, frame and the progressbar
root = Tk()
frame = Frame(root, width=700, height=400, bg=FRAME_COLOR).place(x=CHILDREN_X - 15,
                                                                 y=CHILDREN_Y - 50)  # frame is a diva
progress = Progressbar()

# initialize the strings needed
source_string = StringVar()
destination_string = StringVar()
options_string = StringVar()
download_message = StringVar()


# update the progressbar
def progress_check(stream=None, chunk=None, file_handle=None, remaining=None):
    percentage = (100 * (stream.filesize - file_handle) / stream.filesize)
    print(percentage)
    progress['value'] = int(percentage)
    root.update_idletasks()


# Method is responsible for downloading the yt video if possible
def Downloader():
    # response label
    Label(root, textvariable=download_message, bg=FRAME_COLOR, font='arial 15').place(x=CHILDREN_X,
                                                                                      y=CHILDREN_Y + 250)
    # in case the source is not given
    if str(source_string.get()) == '':
        download_message.set(MISSING_SOURCE)
    # in case the destination is not given
    elif str(destination_string.get()) == '':
        download_message.set(MISSING_PATH)
    # in case the path does not exist
    elif not path.exists(str(destination_string.get())):
        download_message.set(INVALID_PATH)
    # start the download (try at least)
    else:
        try:
            # create YouTube object
            video = YouTube(str(source_string.get()), on_progress_callback=progress_check)
            # in case the user want's to download a mp4 file
            if str(options_string.get()) == OptionList[0]:
                video.streams.filter(file_extension="mp4").first().download(str(destination_string.get()))
            # in case the user want's to download a mp3 file
            elif str(options_string.get()) == OptionList[1]:
                # convert only audio mp4 to mp3, pytube doesnt support mp3 download :-/
                mp4Vid = video.streams.get_audio_only().download(str(destination_string.get()))
                base, ext = os.path.splitext(mp4Vid)
                converted = base + ".mp3"
                os.rename(mp4Vid, converted)
        # no youtube url or unavailable youtube url
        except (RegexMatchError, VideoUnavailable):
            download_message.set(INVALID_SOURCE)
            return None
        except urllib.error.HTTPError:  # found no fix for this error yet -> seems to be random somehow idk
            print("urllib.error.HTTPERROR?????")
            return None
        # in case the download was successful
        download_message.set(DOWNLOAD_SUCCESSFUL)


# initialize the window
def initWindow():
    #####################################################################################################################
    root.geometry('800x500')
    root.resizable(0, 0)
    root.title("Youtube Video Downloader")
    root.configure(background=ROOT_COLOR)
    #####################################################################################################################
    initAndPlaceElements(frame)
    progress.place(x=CHILDREN_X + 150, y=CHILDREN_Y + 220)
    root.mainloop()


# make the client look for a specific directory
def browseDirectory():
    filename = filedialog.askdirectory()
    destination_string.set(filename)


# function creates and start a Download-Thread each times it's called
def create_and_start_download_thread():
    downloadThread_tmp = DownloadThread()
    downloadThread_tmp.start()


# initialize and place the coresponding elements of the window
def initAndPlaceElements(parent):
    #####################################################################################################################
    Label(parent, text='Enter the Video URL in the Field below', font=LABEL_FONT,
          bg=FRAME_COLOR).place(x=CHILDREN_X, y=CHILDREN_Y)
    Entry(parent, width=ENTRY_WIDTH, font=ENTRY_FONT, textvariable=source_string).place(x=CHILDREN_X, y=CHILDREN_Y + 30)
    options_string.set(OptionList[0])
    OptionMenu(parent, options_string, *OptionList).place(x=CHILDREN_X + 410, y=CHILDREN_Y + 30)
    #####################################################################################################################
    Label(parent, text='Enter the destination Path in the Field below', font=LABEL_FONT, bg=FRAME_COLOR).place(
        x=CHILDREN_X,
        y=CHILDREN_Y + 80)
    Entry(parent, width=ENTRY_WIDTH, font=ENTRY_FONT, textvariable=destination_string).place(x=CHILDREN_X,
                                                                                             y=CHILDREN_Y + 110)
    Button(parent, text="Browse Files", command=browseDirectory, bg=BUTTON_COLOR).place(x=CHILDREN_X + 410,
                                                                                        y=CHILDREN_Y + 110)
    #####################################################################################################################
    Button(parent, text='DOWNLOAD', font='arial 15 bold', bg=BUTTON_COLOR,
           command=create_and_start_download_thread).place(
        x=CHILDREN_X,
        y=CHILDREN_Y + 200)
    #####################################################################################################################
    progress.configure(parent, length=400, mode="determinate", orient=HORIZONTAL)


# MAGIC
initWindow()
