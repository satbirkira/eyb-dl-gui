import unittest
from model import Model
from constants import State, Format, Quality, titleFormat, videoState
import os
 
class TestModel(unittest.TestCase):
 
    def setUp(self):
        pass
 
    def test_default_HQ_FLV(self):
        model = Model()
        self.assertEqual(model.program_status, State.NO_OPEN_FILE)
        
    def test_default_use_bookmark_title(self):
        model = Model()
        self.assertEqual(model.output_title_format, titleFormat.USE_BOOKMARK_TITLE)

    def test_default_status(self):
        model = Model()
        self.assertEqual(model.program_status, State.NO_OPEN_FILE)

    def test_gets_and_sets(self):
        model = Model()
        
        model.setFilePath("C:\bookmark.html")
        model.setOutputPath("C:\downloads")
        model.setOutputFormat(Format.WAV)
        model.setOutputTitleFormat(titleFormat.USE_YOUTUBE_TITLE)
        model.setOutputQuality(Quality.HIGH)
        model.setStatus(State.OPENING_FILE)

        self.assertEqual(model.getFilePath(), "C:\bookmark.html")
        self.assertEqual(model.getOutputPath(), "C:\downloads")
        self.assertEqual(model.getOutputFormat(), Format.WAV)
        self.assertEqual(model.getOutputTitleFormat(), titleFormat.USE_YOUTUBE_TITLE)
        self.assertEqual(model.getOutputQuality(), Quality.HIGH)
        self.assertEqual(model.getStatus(), State.OPENING_FILE)

    def test_loading_book_mark_bad(self):
        model = Model()
        
        #test to make sure that if the file does not exist, the state
        #is still NO_OPEN_FILE. We don't check if its EMPTY_FILE since
        #that is just a flag state for the UI to display a error dialog box
        #and instantly changes back to NO_OPEN_FILE after the UI has been informed.
        self.assertEqual(model.getStatus(), State.NO_OPEN_FILE)
        model.loadBookmark("")
        self.assertEqual(model.getStatus(), State.NO_OPEN_FILE)
        self.assertEqual(model.numberOfVideos(), 0)

    def test_loading_book_mark_good(self):
        model = Model()
        
        self.assertEqual(model.getStatus(), State.NO_OPEN_FILE)        
        model.loadBookmark(os.getcwd() + "\\bookmarks.html")
        self.assertEqual(model.getStatus(), State.FILE_OPENED)
        self.assertEqual(model.numberOfVideos(), 1)

    
    def test_video_skip(self):
        model = Model()
       
        model.loadBookmark(os.getcwd() + "\\bookmarks.html")
        #test skipping
        self.assertEqual(model.videoStatus(0), videoState.QUEUED)
        model.removeItemFromList(0)
        self.assertEqual(model.videoStatus(0), videoState.SKIPPED)
        model.queueItemFromList(0)
        self.assertEqual(model.videoStatus(0), videoState.QUEUED)
        #test cancelling
        model.changeVideoStatus(0, videoState.DOWNLOADING)
        model.removeItemFromList(0)
        self.assertEqual(model.videoStatus(0), videoState.CANCELLED)
        #queueing this should not work, should stay canceled
        model.queueItemFromList(0)
        self.assertEqual(model.videoStatus(0), videoState.CANCELLED)

    def test_updating_try_downloading(self):
        model = Model()
        model.setStatus(State.UPDATING)
        model.startDownloading()
        self.assertEqual(model.getStatus(), State.UPDATING)

    #note: this test should fail. add code later to check setters bounds
    def test_correct_bounding_setters(self):
        model = Model()

        original_OutputFormat = model.getOutputFormat()
        original_OutputTitleFormat = model.getOutputTitleFormat()
        original_getOutputQuality = model.getOutputQuality()
        original_Status = model.getStatus()

        #try to set value to one that is not defined as a constant
        model.setOutputFormat(-1)
        model.setOutputTitleFormat(-1)
        model.setOutputQuality(-1)
        model.setStatus(-1)

        self.assertEqual(model.getOutputFormat(), original_OutputFormat)
        self.assertEqual(model.getOutputTitleFormat(), original_OutputTitleFormat)
        self.assertEqual(model.getOutputQuality(), original_getOutputQuality)
        self.assertEqual(model.getStatus(), original_Status)

    #note: this test should fail. add the code later so
    #setters first check program state
    def test_disable_setters_when_downloading(self):
        model = Model()

        model.setFilePath("A")
        model.setOutputPath("A")
        model.setOutputFormat(Format.FLV)
        model.setOutputTitleFormat(titleFormat.USE_BOOKMARK_TITLE)
        model.setOutputQuality(Quality.NORMAL)

        model.setStatus(State.DOWNLOADING)

        model.setFilePath("B")
        model.setOutputPath("B")
        model.setOutputFormat(Format.WAV)
        model.setOutputTitleFormat(titleFormat.USE_YOUTUBE_TITLE)
        model.setOutputQuality(Quality.HIGH)

        self.assertEqual(model.getFilePath(), "A")
        self.assertEqual(model.getOutputPath(), "A")
        self.assertEqual(model.getOutputFormat(), Format.FLV)
        self.assertEqual(model.getOutputTitleFormat(), titleFormat.USE_BOOKMARK_TITLE)
        self.assertEqual(model.getOutputQuality(), Quality.NORMAL)        
        
 
if __name__ == '__main__':
    unittest.main()
