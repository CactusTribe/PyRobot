from time import sleep
from picamera import PiCamera

camera = PiCamera()
camera.resolution = (1024,768)
camera.start_preview()

sleep(1)
camera.capture("foo.jpg")

camera.stop_preview()
camera.close()