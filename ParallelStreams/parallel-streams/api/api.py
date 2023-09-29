from flask import Flask, request, jsonify, Response
from time import sleep
import os
import cv2
import threading

all_data = {"MOS IR": {"Left":0, "Right":0}, "Filter roll": {"Amount left":0}, "Trash pile": {"Height":0}, "IR": {"Count":0}, "Silo Status": {"Status": "Undefined"}}

import sys

# import the models
sys.path.insert(0, '../../../MOSIRcamera')
from MOS_IR_app import MOS_IR_app

sys.path.insert(0, '../../../TrashPile')
from TrashPile_app import TrashPile_app

sys.path.insert(0, '../../../FilterRoll')
from FilterRoll_app import FilterRoll_app

sys.path.insert(0, '../../../Esteban')
from SiloStatusApp import SiloStatusApp

# Helper class for testing
class streamer:
    def __init__(self, stream_addr, name):
        self.stream = cv2.VideoCapture(stream_addr)
        self.name = name

    def read(self):
        ret, frame = self.stream.read()
        return ret, frame, {"Left":0, "Right":0}
    
    def stop(self):
        self.stream.release()

    def get_name(self):
        return self.name
    

# add the models to a list
model_list = [MOS_IR_app(analyze_frame=False), 
              FilterRoll_app(analyze_frame = False), 
              TrashPile_app(analyze_frame = False), 
              SiloStatusApp("C:/Users/jakhs/OneDrive - ROCKWOOL Group/Documents/SandeepAdHoc/Esteban/run3.pt", False)]
models = {model.get_name():model for model in model_list}
infers = [False for _ in range(len(model_list))]

# Flask stuff
app = Flask(__name__)

# Main page
@app.route('/', methods=['GET'])
def root():
    return "Hello World!"

# Get the list of models
@app.route('/models', methods=['GET','POST'])
def get_models():
    response = jsonify(list(models.keys()))
    return {"models":list(models.keys())}#response# Response(response, mimetype='application/json')

# Set the model to start/stop analyzing frames
@app.route('/set_infer', methods=['POST'])
def set_infer():
    global model_list
    model_index = request.get_json()["model_index"]
    assert model_index is not None, "No model index given"

    model_index = int(model_index)

    model_list[model_index].set_analyze_frame(1- infers[model_index])
    infers[model_index] = 1 - infers[model_index]    
    return {True:True}

# Get the data from the models
@app.route('/data', methods=['GET','POST'])
def get_data():
    global all_data
    return all_data

# Get the image from the model with the given id
@app.route('/stream/<id>', methods=['GET'])
def get_stream(id):
    id_num = None
    model = None
    try: 
        id_num = int(id)
    except:
        try:
            model = models[id]
        except:
            raise Exception("Invalid model name")

    
    if id_num is not None:
        assert id_num >= 0 and id_num < len(models), "Invalid id"

        image = get_image_from_id(id_num)
    elif model is not None:
        image = get_image_from_model(model)
    else:
        raise Exception("Neither model nor id is chosen")
    
    return Response(image, mimetype='multipart/x-mixed-replace; boundary=frame')

# Get the image from the model by id
def get_image_from_id(id):
        # vc = cv2.VideoCapture(0)
    print(list(models.keys())[id])
    vc = models[list(models.keys())[id]]
    return get_image_from_model(vc)

# Get the image from the model by name
def get_image_from_model(model):
    global all_data

    # check camera is open
    rval, frame, data = model.read()

    # while streaming
    while rval:
        # read next frame
        rval, frame, data = model.read()
        # if blank frame
        if frame is None:
            continue

        all_data[model.get_name()] = data
        
        #draw text on frame
        # cv2.putText(frame, f"Stream: {id}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 4) 
        # encode the frame in JPEG format
        (flag, encodedImage) = cv2.imencode(".jpg", frame)

        # ensure the frame was successfully encoded
        if not flag:
            continue

        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + encodedImage.tobytes() + b'\r\n')

    # release the camera
    model.stop()


# Run the app
if __name__ == '__main__':
    host = "127.0.0.1"
    port = 5000
    debug = True
    options = None
    #    app.run(host, port, debug, options)
    start = lambda: app.run(host, port, debug, options, threaded=True)

    start()
    # a = threading.Thread(target=start)
    # a.daemon = True
    # a.start()
    # a.join()