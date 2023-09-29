import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt
from torchvision import transforms
import threading
## From example
from time import sleep
import sys
sys.path.insert(0, '../')
from utilities import VideoStream

## Importing the model architecture
from resnet import ResNet

## Config
resize_size_1 = 640 
crop_size = 480
resize_size_2 = 224

class SiloStatusApp(VideoStream):
	def __init__(self, weights_path, infer):
		self.infer = infer
		device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
		self.model = ResNet(num_classes=2)
		self.model.load_state_dict(torch.load(weights_path, map_location = device))
		self.model.eval()
		# self.stream = cv2.VideoCapture("rtsp://Viewer:Only4FOF!@MOS-CCTV-Process.rwgroup.org:8554/1649152")
		# self.stream = cv2.VideoCapture("rtsp://admin:fof2022venom@10.6.132.13")
		self.stream = cv2.VideoCapture("../fake_feeds/esteban_fake.mp4")

		self.state = "Filling"
		self.preprocess = transforms.Compose([
        										transforms.ToPILImage(),
												transforms.Resize(resize_size_1),
												transforms.CenterCrop(crop_size),
												transforms.Resize(resize_size_2),
												transforms.ToTensor()])
		self.labels = ['Filled', 'Filling']

		self.image = None
		self.thread = threading.Thread(target=self.consume)
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

	def get_name(self) -> str:
		return "Silo Status"

	def read(self) -> (bool, object, dict):
		# assert self.stream.isOpened(), "Cannot open video"
		# ret, frame = self.stream.read()
		ret, frame = not self.image is None, self.image
		if not self.infer:
			return ret, frame if ret else None, None
		else:
			processed_frame = self.analyze(frame)
			return ret, processed_frame if ret else None, {"Status" : self.state}
	

	def analyze(self, frame) -> None:
		preprocessed_frame = self.preprocess(frame)
		# Perform inference
		with torch.no_grad():
			input_tensor = preprocessed_frame.unsqueeze(0)
			output = self.model(input_tensor)

		# Get the predicted class label
		predicted_class = torch.argmax(output, dim=1).item()
		predicted_label = self.labels[predicted_class]

		self.state = predicted_label

		# Draw the predicted class label on the frame
		if predicted_label == "Filling":
			cv2.putText(frame, predicted_label , (75, 230), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)

		if predicted_label == "Filled":
			cv2.putText(frame, predicted_label , (75, 230), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)

		cv2.putText(frame, "Status:" , (50, 170), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)
		# cv2.putText(frame, f" Predictions: {output}" , (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
		return frame
	
	def stop(self) -> None:
		# Stop you model, close the video stream etc.
		self.stream.release()	

	def set_analyze_frame(self, infer) -> None:
		# Should set "self.analyze_frame"
		# if self.analyze_frame is False, read() should return a frame without any analysis 
		self.infer = infer

	def get_data_string(self) -> str:
		# return a string of data to be displayed on the web page
		pass