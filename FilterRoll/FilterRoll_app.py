
import numpy as np
import matplotlib.pyplot as plt
import cv2
import threading
from time import sleep

import sys
sys.path.insert(0, '../')
from utilities import VideoStream
# empty, full = cv2.imread('empty.png'), cv2.imread('full.png') 


cutout_size = {'x':(630,1000), 'y':(500,1100)} 
cutout = lambda img: img[cutout_size['x'][0]:cutout_size['x'][1], cutout_size['y'][0]:cutout_size['y'][1]]



class FilterRoll_app(VideoStream):
    def __init__(self, analyze_frame):
        self.analyze_frame = analyze_frame
        # self.stream = cv2.VideoCapture("C:/Users/jakhs/OneDrive - ROCKWOOL Group/Documents/SandeepAdHoc/FilterRoll/combined_filter_roll-short.mp4")
        self.stream = cv2.VideoCapture("rtsp://Viewer:Only4FOF!@MOS-CCTV-Process.rwgroup.org:8554/1649152")
        # self.stream = cv2.VideoCapture("rtsp://admin:fof2022venom@10.6.132.13")
        # self.stream = cv2.VideoCapture("../fake_feeds/filter_roll_fake.mp4")

        self.how_filled = "Filter capacity good"
        self.amount_filled = 0

        self.thread = threading.Thread(target=self.consume)

        self.thread.start()
        self.image = None
        self.has_analyzed = False

    def consume(self):
        try:
            while True:
                sleep(0.3)
                ret, frame = self.stream.read()
                if ret:
                    self.image = frame
                    self.has_analyzed = False
                else:
                    self.image = None
        except cv2.error as e:
                print("Error in reading frame")
                print(e)

    def read(self):
        ret, frame = not self.image is None, self.image

        if not self.analyze_frame or not ret:
            return ret, frame if ret else None, None
        else:
            return ret, self.analyze(frame) if ret else None, {"Amount left" : self.amount_filled}

    def set_analyze_frame(self, analyze_frame): 
        self.analyze_frame = analyze_frame

    def stop(self):
        self.stream.release()

    def get_name(self):
        return "Filter roll"


    def get_data_string(self):
        # if self.analyze_frame:
        #     assert self.stream.isOpened(), "Cannot open video"
        #     ret, frame = self.stream.read()
        #     self.analyze(frame)

        return f"FilterRoll\n{self.how_filled}"

    def analyze(self, frame):

        if self.has_analyzed:
            return frame
        # cut out important part
        img = cutout(frame)

        # convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # apply threshold
        threshold = 220
        gray = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)[1]
        
        # find contours
        contours, hierarchy = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # find largest contour
        contour = max(contours, key=cv2.contourArea)

        # find bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)

        full = w > 450


        # draw contours
        img = cv2.drawContours(img, contours, -1, (100, 0, 0), 1)

        color = (0, 255, 0) if full else (0, 0, 255)

        img = cv2.drawContours(img, contour, -1, color, 4)


        # draw bounding rectangle
        # if full:
        #     img = cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        # else:
        #     img = cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)


        area = cv2.contourArea(contour) / 10000

        txt = "Filter capacity good"
        txt_col = (255,100,100)
        if not full:
            txt = "Roll empty!"
            txt_col = (0,0,255)
        else:
            if area < 1.5:
                txt = "Running low"
                txt_col = (0,255,255)
            
        img = cv2.fillPoly(img, pts =[contour], color=txt_col)

        self.how_filled = txt

        self.amount_filled = area
        # draw text of contour area

        # place cutout back in frame
        frame[cutout_size['x'][0]:cutout_size['x'][1], cutout_size['y'][0]:cutout_size['y'][1]] = img

        cv2.putText(frame, txt, (300, 300), cv2.FONT_HERSHEY_SIMPLEX, 4, (0,0,0), 10) 
        cv2.putText(frame, txt, (300, 300), cv2.FONT_HERSHEY_SIMPLEX, 4, txt_col, 4) 

        self.has_analyzed = True

        return frame




