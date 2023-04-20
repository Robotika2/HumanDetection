import time, cv2
import matplotlib.pyplot as plt
from threading import Thread
from queue import Queue
from djitellopy import Tello
import threading
import logging

from pretrained import model, convert_to_tensor, process_data, compute_dev

tello = Tello()
tello.LOGGER.setLevel(logging.DEBUG)

time.sleep(3)
tello.connect()
tello.streamon()
frame_read = tello.get_frame_read()
deviation = None

def videoRecorder():
    while run:
        image = frame_read.frame

        torch_tensor = convert_to_tensor(image)

        output = model(torch_tensor)
        result = process_data(output, image)
        y_dev, x_dev = compute_dev(result)


        cv2.imshow("output_drone", image)
        if cv2.waitKey(1) == ord('q'):
            run = False
            break

tello.streamon()

recorder = Thread(target=videoRecorder)
recorder.start()


tello.takeoff()
"""
tello.rotate_counter_clockwise(360)
tello.land()
keepRecording = False
recorder.join()
"""