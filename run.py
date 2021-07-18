import detect_aruco_video
from bluetooth import * 

import threading

val = "2"

loop = asyncio.get_event_loop()
bluetoothThread = threading.Thread(target=start, args=(loop, ))
bluetoothThread.start()

detect_aruco_video.start()