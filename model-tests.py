import unittest
from model import Model
from constants import State, Format, Quality, titleFormat, videoState

 
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




 
if __name__ == '__main__':
    unittest.main()
