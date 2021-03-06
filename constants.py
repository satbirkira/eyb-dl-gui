class State:
    NO_OPEN_FILE = 0
    EMPTY_FILE = 1
    OPENING_FILE = 2
    FILE_OPENED = 3
    DOWNLOADING = 4
    UPDATING = 5
    YTDL_UPDATE_FAIL = 6
    YTDL_UPDATE_SUCCESS = 7
    INVALID_OUTPUT_PATH = 8
    COMPLETE = 9
    toString = {0: "No Open File",
                1: "Empty File",
                2: "Opening File",
                3: "File Opened",
                4: "Downloading",
                5: "Updating",
                6: "Youtube Downloader Update Failed",
                7: "Youtube Downloader Update Success",
                8: "Invalid Output Path",
		9: "Downloads Complete"}

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
    DOWNLOADING = 3
    ERROR = 4
    COMPLETE = 5
    toString = {0: "Queued",
                1: "Skip",
                2: "Cancelled",
                3: "Downloading",
                4: "Error",
                5: "Complete"}
