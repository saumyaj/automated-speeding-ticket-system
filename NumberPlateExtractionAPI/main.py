import cv2 as cv
import argparse
import sys
import numpy as np
import os.path
import boto3
import base64
import time
from google.cloud import storage
from flask import request

from flask import Flask
app = Flask(__name__)


# import the necessary packages
import urllib
# METHOD #1: OpenCV, NumPy, and urllib

# def url_to_image(url):
#     # download the image, convert it to a NumPy array, and then read
#     # it into OpenCV format
#     resp = urllib.request.urlopen(url)
#     print(resp.geturl())
#     # print(resp.read())
#     image = np.asarray(bytearray(resp.read()), dtype="uint8")
#     image = cv.imdecode(image, cv.IMREAD_COLOR)
#     # return the image
#     return image

# Initialize the parameters
confThreshold = 0.5  #Confidence threshold
nmsThreshold = 0.4  #Non-maximum suppression threshold

inpWidth = 416  #608     #Width of network's input image
inpHeight = 416 #608     #Height of network's input image


# Get the names of the output layers
def getOutputsNames(net):
    # Get the names of all the layers in the network
    layersNames = net.getLayerNames()
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# Draw the predicted bounding box
def drawPred(frame, classes, classId, conf, left, top, right, bottom):
    # Draw a bounding box.
    #    cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)
    cv.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)

    label = '%.2f' % conf

    # Get the label for the class name and its confidence
    if classes:
        assert(classId < len(classes))
        label = '%s:%s' % (classes[classId], label)

    #Display the label at the top of the bounding box
    labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    top = max(top, labelSize[1])
    cv.rectangle(frame, (left, top - round(1.5*labelSize[1])), (left + round(1.5*labelSize[0]), top + baseLine), (0, 0, 255), cv.FILLED)
    #cv.rectangle(frame, (left, top - round(1.5*labelSize[1])), (left + round(1.5*labelSize[0]), top + baseLine),    (255, 255, 255), cv.FILLED)
    cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 2)

    crop_img = frame[top:bottom, left:right]
    # cv.imshow("cropped", crop_img)
    # cv.imwrite("cropped.jpg", crop_img)
    # cv2.waitKey(0)
    return detect_text(crop_img)


def detect_text(crop_img):
    ACCESS_KEY = 'AKIATSOACSKSXBCAOSWC'
    SECRET_KEY = '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'
    client=boto3.client('rekognition',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name='us-west-2')


    success, encoded_image = cv.imencode('.png', crop_img)
    # print(type(encoded_image))

    content2 = encoded_image.tobytes()
    # print(type(content2))

    response=client.detect_text(Image={'Bytes':content2})

    license_plate = response['TextDetections'][0]['DetectedText']
    return license_plate
    # input('')


# Remove the bounding boxes with low confidence using non-maxima suppression
def postprocess(frame, classes, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]

    classIds = []
    confidences = []
    boxes = []
    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    classIds = []
    confidences = []
    boxes = []
    for out in outs:
        # print("out.shape : ", out.shape)
        for detection in out:
            # print(detection)
            # print(confThreshold)
            # input('')
            #if detection[4]>0.001:
            scores = detection[5:]
            classId = np.argmax(scores)
            #if scores[classId]>confThreshold:
            confidence = scores[classId]
            if detection[4]>confThreshold:
                pass
                # print(detection[4], " - ", scores[classId], " - th : ", confThreshold)
                # print(detection)
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)

    license_plate = 'not updated'
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        license_plate = drawPred(frame, classes, classIds[i], confidences[i], left, top, left + width, top + height)
    return license_plate

def main(filename):
    # print('file: ' + filename)

    # request_json = request.json
    # source_blob_name = request_json['image_name']
    source_blob_name = filename

    json_path = 'cc2020-storage-api.json'
    bucket_name = 'fast_cars'
    # source_blob_name = 'lamb.jpg'
    destination_file_name = source_blob_name

    storage_client = storage.Client.from_service_account_json(json_path)

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    frame = cv.imread(destination_file_name)

    # url = 'https://storage.cloud.google.com/fast_cars/lamb.jpg'
    # # url = 'https://00e9e64bacdfa1c18f8ce0ddc8527c105cd5213b99146dcf5f-apidata.googleusercontent.com/download/storage/v1/b/fast_cars/o/lamb.jpg?qk=AD5uMEupj59LDLZTWsKcaX6017ByDTvfCRhtKegVDtd0bJxKgkcjWGfhQtvwSOMV2F_fs5_gn_nqzS5gE2WCbR5865mBGSBb2WDp_nXlUzPE66npdIR6NSAobdg2yQlvspC-xnaNcf7ghzUUuOkYxsL_b5UOc7kgo7ZPhj7-QGN6oltOCyHoH5pHaeVGNsYrpOgEQwkz02cmrdVkmm6WQh0wu23lIhOibTIHCDh6V7MXnFw8utqj2qnEu_TOsQiLeAs9IVgZuasJqYqp1CDEhsDeEOnxdcnomh2MAn20pkvwGKSyxvsfzDXDx4TH0P4FIj87bOsix_8CPnMVqoR5u2msJT_D06RxrsvRSlzr6gckvjeqPiya932qTjXe3ZnA704nhdv6-9C8V3v14_C0s8GWzD3K0totsKwsbS8Xiw7BPnzozU8JSStcrtLpdrHsBPTuLAYO-TgDBvRVA7H8WuVm7GAnZj9-Fx1DA9gVpHgH1qEottrGa7lybpYL8aH4c-XzJoH3NtTkVWMZVRJyb1keKPvCTUBsLKt07tKzfA8bhSNTd1oPAtXh2au4jrnB5wUfv0nC9RhVjUsRUbEgwRIdedhuowMDsGzIVy6OZMZIjHAv0KtKZ0lQUsTm5lIjFH9NrXjyVUZo0MkCiL2D0yuNq-cX0Gn_pv8QqGrXewAvTTHSwIL8hufcTZloMk04Qno4ju4PJrR-hLKd4nMI36e6lpFcBqSmvcTPidX8_MHNgxQLdd42sDe_6ui5ubJis1du9Xpa84IeI-kXLHRQ3H2Cx4VP3eZgWg&isca=1'
    # img = url_to_image(url)
    # print(type(img))
    # input('')

    # with open("lamb.jpg", "rb") as img_file:
    #     img_data = base64.b64encode(img_file.read())

    # print(type(img_data))

    # # request_json = request.json()
    # img_data_str = str(img_data)

    # # print(type(img_data_str))
    # # img_data = request_json['image_bytes']
    # time_integer = int(time.time() * 1e6)

    # # img_bytes = img_data_str.decode('base64')





    # # image_byte_str = img_data_str.encode('utf-8')
    # img_bytes = str.encode(img_data_str)


    # message_bytes = base64.b64decode(img_bytes)
    # # message = message_bytes.decode('utf-8')
    # print(type(message_bytes))
    # input('')


    # decoded = cv.imdecode(np.frombuffer(img_bytes, np.uint8), -1)
    # print(type(decoded))
    # input('')


    # if request.args and 'message' in request.args:
    #     return request.args.get('message')
    # elif request_json and 'message' in request_json:
    #     return request_json['message']
    # else:
    #     return f'Hello World!'



    parser = argparse.ArgumentParser(description='Object Detection using YOLO in OPENCV')
    parser.add_argument('--image', help='Path to image file.')
    parser.add_argument('--video', help='Path to video file.')
    args = parser.parse_args()

    # Load names of classes
    classesFile = "classes.names";

    classes = None
    with open(classesFile, 'rt') as f:
        classes = f.read().rstrip('\n').split('\n')

    # Give the configuration and weight files for the model and load the network using them.

    modelConfiguration = "darknet-yolov3.cfg";
    modelWeights = "lapi.weights";

    net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

    # Process inputs
    # winName = 'Deep learning object detection in OpenCV'
    # cv.namedWindow(winName, cv.WINDOW_NORMAL)

    # Create a 4D blob from a frame.
    blob = cv.dnn.blobFromImage(frame, 1/255, (inpWidth, inpHeight), [0,0,0], 1, crop=False)

    # Sets the input to the network
    net.setInput(blob)

    # Runs the forward pass to get output of the output layers
    outs = net.forward(getOutputsNames(net))

    # Remove the bounding boxes with low confidence
    license_plate = postprocess(frame, classes, outs)

    # Put efficiency information. The function getPerfProfile returns the overall time for inference(t) and the timings for each of the layers(in layersTimes)
    t, _ = net.getPerfProfile()
    label = 'Inference time: %.2f ms' % (t * 1000.0 / cv.getTickFrequency())
    #cv.putText(frame, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
    # outputFile = args.image[:-4]+'_yolo_out_py.jpg'
    # cv.imwrite(outputFile, frame.astype(np.uint8));

    return license_plate

@app.route('/')
def hello_world():
    filename = request.args.get('filename',None)
    return main(filename)

if __name__ == '__main__':
    app.run()