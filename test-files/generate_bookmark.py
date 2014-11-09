import string
import os
import random

file_name = "bookmark_1k_bomb.html"

text = ""
print("Generating..")
for i in range(1, 1000):
    random_video_id = ''.join(random.choice(string.ascii_uppercase) for i in range(8))
    random_ADD_DATE = ''.join(random.choice(string.ascii_uppercase) for i in range(10))
    random_ICON = ''.join(random.choice(string.ascii_uppercase) for i in range(557))
    random_NAME = ''.join(random.choice(string.ascii_uppercase) for i in range(37))
    video = "<DT><A HREF=\"https://www.youtube.com/watch?v="+random_video_id+"\" ADD_DATE=\""+random_ADD_DATE+"\" ICON=\"data:image/png;base64,"+random_ICON+"\">"+random_NAME+"</A>\n"
    text += video
file = open(file_name, 'w', encoding='utf8')
file.write(text)
file.close()

        
