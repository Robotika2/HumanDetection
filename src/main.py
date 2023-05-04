import time, cv2
import matplotlib.pyplot as plt
from threading import Thread
from queue import Queue
from djitellopy import Tello
import logging

from pretrained import model, convert_to_tensor, process_data, compute_dev, SCREEN_CENTER

tello = Tello()
#tello.LOGGER.setLevel(logging.DEBUG)

instructions = Queue()

time.sleep(3)
tello.connect()
tello.streamon()
frame_read = tello.get_frame_read()

#functions
def Convert_to_Instructions(y_deviation, x_deviation, ob_area):
    #recompute to linear scale (lol)

    if x_deviation > 0.8:
        #compute rotation
        in1 = ["rotate", int(round(abs(x_deviation - 0.5) * 90))]
    else:
        in1 = []

    if ob_area > 0.8:
        #compute baackward shift
        in2 = ["backward", 20]
    else:
        #compute forward shift
        in2 = ["forward", int(round(ob_area * 200))]

    return [in2, in1]

def stop_drone():
    tello.land()
    instructor.join()
    exit(1)

def videoRecorder():
    image = frame_read.frame

    torch_tensor = convert_to_tensor(image)

    output = model(torch_tensor)
    result = process_data(output, image)
    if len(result) != 0: #just when the data is avaliable
        y_dev, x_dev, area = compute_dev(result, image)

        y_dev = round(y_dev / SCREEN_CENTER[0], 2)
        x_dev = round(x_dev / SCREEN_CENTER[1], 2)

        instruction = Convert_to_Instructions(y_dev, x_dev, area)
        print("IN:")
        print(instruction)

        instructions.put(instruction)

    cv2.imshow("output_drone", image)
    if cv2.waitKey(1) == ord('q'):
        stop_drone()

def process_instructions():
    while True: #i hate this
        instruction = instructions.get()
        with instructions.mutex:
            instructions.queue.clear()

        if len(instruction) == 0:
            continue

        if instruction[0][0] == "forward":
            tello.move_forward(instruction[0][1])
        else:
            tello.move_back(instruction[0][1])

        """
        if instruction[0] == "up-down":
            pass #TODO: dodělat!
        """
        if len(instruction[1]) == 0:
            if instruction[1][0] == "rotate":
                if instruction[1][1] <= 0:
                    #left
                    tello.rotate_counter_clockwise(instruction[1][1])
                else:
                    #right
                    tello.rotate_clockwise(instruction[1][1])
            
            else:
                pass

        print("OUT:")
        print(instruction)

instructor = Thread(target=process_instructions)
instructor.start()

tello.takeoff()
tello.move_up(100)

while True:
    videoRecorder()