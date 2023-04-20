from torchvision.models import detection
from torchvision import transforms
import torch
import cv2

#my imports
from pretrained import model, convert_to_tensor, process_data

vid = cv2.VideoCapture(0)
  
while(True):
    ret, frame = vid.read()
    torch_tensor = convert_to_tensor(frame)

    output = model(torch_tensor)
    result = process_data(output, frame)
    
    print(result)
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid.release()
cv2.destroyAllWindows()