import cv2 
import numpy as np

import matplotlib.patheffects as pe
import threading

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from time import sleep
import sys
# sys.path.insert(0, '../')
sys.path.insert(0, 'C:/Users/jakhs/OneDrive - ROCKWOOL Group/Documents/SandeepAdHoc/')
from utilities import VideoStream

class MOS_IR_app(VideoStream):
    def __init__(self, analyze_frame):
        self.analyze_frame = analyze_frame
        
        self.x_lim = (350,1100-200)
        self.y_lim = (50,470)

        self.mid = int((self.x_lim[0] + self.x_lim[1])/2) + 80
        self.measure_y = (320,400)

        self.polygon = Polygon([(self.x_lim[0], self.measure_y[0] - 10), (self.x_lim[1],self.measure_y[0] + 20), (self.x_lim[1],self.measure_y[1] - 30), (self.x_lim[0], self.measure_y[1])])

        self.spots = []
        self.left = 0
        self.right = 0

        # self.stream = cv2.VideoCapture("MOS_IR.avi")
        # self.stream = cv2.VideoCapture("rtsp://Viewer:Only4FOF!@MOS-CCTV-Process.rwgroup.org:8554/1638912")
        # self.stream = cv2.VideoCapture("rtsp://admin:fof2022venom@10.6.132.13")
        self.stream = cv2.VideoCapture("../fake_feeds/mos_ir_fake.mp4")


        self.image = None
        self.count = 0

        self.thread = threading.Thread(target=self.consume)
        # self.thread.daemon = True
        self.thread.start()

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
        # ret, frame = self.stream.read()
        ret, frame = not self.image is None, self.image

        # if not ret:
        #     self.count += 1
        #     print(self.count)
        #     if self.count > 10:
        #         self.stream.release()
        #         self.stream = cv2.VideoCapture("rtsp://Viewer:Only4FOF!@MOS-CCTV-Process.rwgroup.org:8554/1638912")
        #         self.count = 0

        if not self.analyze_frame:
            return ret, frame if ret else None, None
        
        return ret, self.analyze(frame) if ret else None, {"Left":self.left, "Right":self.right}

    # def get_format_string(self):
    #     return f"MOS IR\nLeft: {}\nRight: {}"
    def get_data_string(self):
        # if self.analyze_frame:
        #     assert self.stream.isOpened(), "Cannot open video"
        #     ret, frame = self.stream.read()
        #     self.analyze(frame)
        return f"MOS IR:\nLeft: {self.left} | Right: {self.right}"

    def set_analyze_frame(self, analyze_frame):
        self.analyze_frame = analyze_frame

    def stop(self):
        self.stream.release()
        
    def analyze(self, f):
        
        # fc = f[y_lim[0]:y_lim[1],x_lim[0]:x_lim[1]].copy()
        fc = f.copy()

        mask = cv2.threshold(fc, 240, 255, cv2.THRESH_BINARY)[1]
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


        # find centers of contours

        important_contours = []
        found_spots_l = []
        found_spots_r = []
        for c in contours:
            M = cv2.moments(c)
            if M["m00"] == 0:
                continue
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"]) 
            if not (cY > self.y_lim[0] and cY < self.y_lim[1] and cX > self.x_lim[0] and cX < self.x_lim[1]):
                continue


            important_contours.append(c)
            point = Point(cX, cY)

            if self.polygon.contains(point):
                self.spots.append(cX)
                
                if cX > self.mid:
                    found_spots_l.append(c)
                    self.left += 1
                else:
                    found_spots_r.append(c)
                    self.right += 1

        cv2.drawContours(fc, important_contours, -1, (0,255,0), 3)
        cv2.drawContours(fc, found_spots_r, -1, (255,0,0), 3)
        cv2.drawContours(fc, found_spots_l, -1, (0,0,255), 3)

        cv2.rectangle(fc, (self.x_lim[0], self.y_lim[0]), (self.x_lim[1], self.y_lim[1]), (100, 100, 100), 2)
        
        # cv2.rectangle(fc, (x_lim[0], measure_y[0]), (x_lim[1], measure_y[1]), (200, 200, 200), 2)
        cv2.polylines(fc, np.int32([np.array(self.polygon.exterior.coords)]), True, (200, 200, 200), 2)


        cv2.line(fc, (self.mid, self.measure_y[0] + 10), (self.mid, self.measure_y[1] - 25), (200, 200, 200), 2)

        # ax1.text(1300, 200, f"Left: {left}", color = 'white', fontsize = 20, path_effects=[pe.withStroke(linewidth=5, foreground="blue")])
        # ax1.text(1300, 300, f"Right: {right}", color = 'white', fontsize = 20, path_effects=[pe.withStroke(linewidth=5, foreground="red")])
        # same text but in cv2 
        cv2.putText(fc, f"Left: {self.left}", (1300, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(fc, f"Right: {self.right}", (1300, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        return fc
    
    def get_name(self):
        return "MOS IR"