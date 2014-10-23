import unittest
from mvc import Model
from mvc import State, Format, Quality, titleFormat, videoState
 
class TestUM(unittest.TestCase):
 
    def setUp(self):
        pass
 
    def test_default_HQ_FLV(self):
        self.assertEqual(Format.FLV, Format.FLV)

 
if __name__ == '__main__':
    unittest.main()
