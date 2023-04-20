from torchvision.models import detection
from torchvision import transforms
import torch
import cv2

DEVICE = "cpu"

model = detection.ssdlite320_mobilenet_v3_large(pretrained=True, progress=True,
	num_classes=91, pretrained_backbone=True).to(DEVICE)
model.eval()

tensor_transform = transforms.ToTensor()

def convert_to_tensor(frame):
    torch_tensor = tensor_transform(frame)
    torch_tensor = torch.unsqueeze(torch_tensor, dim=0)

    return torch_tensor

def process_data(output, frame):
    output = output[0]
    detect_coords = []

    for i in range(len(output["boxes"])):
        confidence = output["scores"][i]
        label = output["labels"][i]

        if confidence >= 0.9 and label == 1: #only detect humans
            box = output["boxes"][i].detach().cpu().numpy()
            (startX, startY, endX, endY) = box.astype("int")

            cv2.rectangle(frame, (startX, startY), (endX, endY), (255, 0, 0), 2)

            detect_coords.append([startX, startY, endX, endY])

    return detect_coords