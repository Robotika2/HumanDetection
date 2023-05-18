import time, cv2
import matplotlib.pyplot as plt
from threading import Thread
from queue import Queue
from djitellopy import Tello

from pretrained import model, convert_to_tensor, process_data, compute_dev, SCREEN_CENTER

tello = Tello()

instructions = Queue()

time.sleep(3)
tello.connect()
tello.streamon()
frame_read = tello.get_frame_read()

#functions
def Convert_to_Instructions(y_deviation, x_deviation, ob_area):
    #recompute to linear scale (lol)

    if abs(x_deviation) > 0.25:
        #compute rotation
        in1 = ["rotate", int(round(x_deviation * 12))]
    else:
        in1 = []

    if ob_area > 0.8:
        #compute baackward shift
        in2 = ["backward", 50]
    else:
        #compute forward shift
        in2 = ["forward", 20 if int(round(ob_area * 50)) <= 20 else int(round(ob_area * 50))]

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
        #print("IN:")
        #print(instruction)

        instructions.put(instruction)
    else:
        instructions.put([[], ["rotate", 25]])

    cv2.imshow("output_drone", image)
    if cv2.waitKey(1) == ord('q'):
        stop_drone()

def process_instructions():
    while True: #i hate this
        instruction = instructions.get()
        with instructions.mutex:
            instructions.queue.clear()

        time.sleep(0.1)
        print(instruction)

        if instruction[0] == "None":
            tello.rotate_clockwise(25)
    
        if instruction[0][0] == "forward":
            tello.send_rc_control(0, instruction[0][1], 0, 0)
        elif instruction[0][0] == "backward":
            tello.send_rc_control(0, -instruction[0][1], 0, 0)

        """
        if instruction[0] == "up-down":
            pass #TODO: dodělat!
        """

        if len(instruction[1]) != 0:
            if instruction[1][0] == "rotate":
                if instruction[1][1] >= 0:
                    #left
                    tello.rotate_clockwise(instruction[1][1])
                else:
                    #right
                    tello.rotate_counter_clockwise(instruction[1][1])
            
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