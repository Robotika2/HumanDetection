from torchvision.models import detection
from torchvision import transforms
import torch
import cv2

#my imports
from pretrained import model, convert_to_tensor, process_data, compute_dev, SCREEN_CENTER

vid = cv2.VideoCapture(0)
  
while(True):
    ret, frame = vid.read()
    torch_tensor = convert_to_tensor(frame)

    output = model(torch_tensor)
    result = process_data(output, frame)
    
    if len(result) != 0: #just when the data is avaliable
        y_dev, x_dev, area = compute_dev(result, frame)

        y_dev = round(y_dev / SCREEN_CENTER[0], 2)
        x_dev = round(x_dev / SCREEN_CENTER[1], 2)

        print(y_dev, x_dev, area)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid.release()
cv2.destroyAllWindows()