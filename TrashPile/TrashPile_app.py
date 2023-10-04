from PIL import Image
import torch
import os 
import matplotlib.pyplot as plt
import numpy as np
from transformers import OwlViTProcessor, OwlViTForObjectDetection
from PIL import ImageDraw
from PIL import ImageFont
import threading
import cv2
from time import sleep

import sys
sys.path.insert(0, '../')
from utilities import VideoStream

processor = OwlViTProcessor.from_pretrained("google/owlvit-base-patch32")
model = OwlViTForObjectDetection.from_pretrained("google/owlvit-base-patch32")

stand_texts = [["a pile of gravel", "a mound of dirt", "a mound of trash", "a pile of rocks"]]

t_small = [ text.split(" ")[0] + " small " + " ".join(text.split(" ")) for text in stand_texts[0]]
t_large = [ text.split(" ")[0] + " large " + " ".join(text.split(" ")) for text in stand_texts[0]]

texts = [t_small] #[stand_texts[0] + t_small + t_large]
x_lim = (500,1100)
y_lim = (10,900)

def cutout(image):
    image = np.array(image)
    cropped = image[y_lim[0]:y_lim[1],x_lim[0]:x_lim[1]]
    return cropped

class TrashPile_app(VideoStream):
    def __init__(self, analyze_frame):
        self.analyze_frame = analyze_frame
        # self.stream = cv2.VideoCapture("C:/Users/jakhs/OneDrive - ROCKWOOL Group/Documents/SandeepAdHoc/TrashPile/avfall.mp4")
        # self.stream = cv2.VideoCapture("rtsp://Viewer:Only4FOF!@MOS-CCTV-Process.rwgroup.org:8554/1645568")
        # self.stream = cv2.VideoCapture("rtsp://admin:fof2022venom@10.6.132.13:554/ch1/main/av?stream")
        self.stream = cv2.VideoCapture("C:/Users/jakhs/OneDrive - ROCKWOOL Group/Documents/MergedModelViewV2/fake_feeds/trash_pile_fake.mp4")

        width = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.last_height = None

        self.print_str = ""
        print(width, height)

        self.thread = threading.Thread(target=self.consume)
        self.thread.start()
        self.image = None

    def consume(self):
        try:
            while True:
                sleep(0.3)
                ret, frame = self.stream.read()
                if ret:
                    self.image = frame
                else:
                    self.image = None
        except cv2.error as e:
                print("Error in reading frame")
                print(e)

    def read(self):
        # assert self.stream.isOpened(), "Cannot open video"
        # ret, frame = self.stream.read()
        ret, frame = not self.image is None, self.image
        # print(ret)
        if not self.analyze_frame:
            return ret, frame if ret else None, None

        if ret:
            analyzed_frame, height, warning = self.analyze(frame)
        else:
            analyzed_frame = None

        return ret, analyzed_frame, {"Height":self.last_height}

    def set_analyze_frame(self, analyze_frame):
        self.analyze_frame = analyze_frame

    def get_name(self):
        return "Trash pile"

    def get_data_string(self):
        # if self.analyze_frame:
        #     assert self.stream.isOpened(), "Cannot open video"
        #     ret, frame = self.stream.read()
        #     self.analyze(frame)
        return f"Trash Pile:\n{self.print_str}"


    def stop(self):
        self.stream.release()   

    # def get_format_string(self):
    #     return f"Trash Pile\nHeight: {:.2} m"
    
    def analyze(self, frame):
        global texts
        image = Image.fromarray(cutout(frame))
        inputs = processor(text=texts, images=image, return_tensors="pt")

        outputs = model(**inputs)

        target_sizes = torch.Tensor([image.size[::-1]])

        
        results = processor.post_process(outputs=outputs, target_sizes=target_sizes)

        i = 0  
        text = texts[i]
        boxes, scores, labels = results[i]["boxes"], results[i]["scores"], results[i]["labels"]

        # sort the boxes and associated scores in descending order
        scores, idxs = scores.sort(descending=True)
        scores  = scores.detach().numpy()
        boxes   = boxes[idxs].detach().numpy()
        labels  = labels[idxs].detach().numpy()
        draw    = ImageDraw.Draw(image)

        box = boxes[0]

        height = box[1]
        if self.last_height != None:
            height = (height + 4*self.last_height) / 5
            box[1] = height

        self.last_height = height
        # height = box[1]
        # for box, score, label in zip(boxes, scores, labels):

        WARNING = False
        if height < 50:
            WARNING = True
            txt = "Overfull!!"
            color = "red"
        elif height < 200:
            txt = "Filling up!"
            color = "orange"
        else:
            txt = "All good :)"
            color = "green"

        self.print_str = txt + f"\nHeight: {height:.2f}"
        #     print(texts[i][label.numpy()])
        draw.rectangle(box, outline= color, width=10)

     

        # draw text on the image
        draw.text((300, 700), text= txt , fill=color, font=ImageFont.truetype("arial", 75))

        # convert PIL image to numpy array
        image = np.array(image)

        # add the image back in the frame
        frame[y_lim[0]:y_lim[1], x_lim[0]:x_lim[1]] = image

        # draw the xlim and ylim as a rectangle
        cv2.rectangle(frame, (x_lim[0], y_lim[0]), (x_lim[1], y_lim[1]), (200, 200, 200), 1)

        return frame, height, WARNING
    

if __name__ == "__main__":
    app = TrashPile_app(analyze_frame=False)
    while True:
        ret, frame = app.read()
        if not ret:
            break
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()