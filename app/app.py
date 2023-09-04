import os
import torch
import cv2
import numpy as np
from flask import Flask, render_template, request, session, jsonify
import requests
from super_gradients.training import models
import supervision as sv
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import json
import base64
from werkzeug.utils import secure_filename
import secret

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Retrieve the secret key from the environment variable
secret_key = secret.secret_key

# Set the secret key for session management
app.secret_key = secret_key

model_arch = 'yolo_nas_l'
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
classes = ['ear protection', 'hard hat', 'high visibility vest', 'mask', 'no glove', 'no helmet', 'no safety boot', 'no vest', 'safety boot', 'safety glasses', 'safety gloves']

#Load the model outside the route function to load it only once
model = models.get(model_arch, num_classes=len(classes), checkpoint_path=r"C:\Users\edw75\test\model_train\ckpt_best.pth")
model.to(device)
model.eval()

def perform_inference(image):
    #Perform inference using the model's predict function
    result = model.predict(image, conf=0.5)[0]
    detections = sv.Detections(
        xyxy=result.prediction.bboxes_xyxy,
        confidence=result.prediction.confidence,
        class_id=result.prediction.labels.astype(int)
    )
    return detections

def visualize_detections(image, detections):
    annotated_image = image.copy()

    box_annotator = sv.BoxAnnotator()

    labels = [
        f"{classes[class_id]} {confidence:.2f}"
        for class_id, confidence
        in zip(detections.class_id, detections.confidence)
    ]
    annotated_image = box_annotator.annotate(image.copy(), detections=detections, labels=labels)

    return annotated_image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST', 'GET'])
def uploadFile():
    if request.method == 'POST':
        if 'uploaded-file' in request.files:
            uploaded_file = request.files['uploaded-file']
            if uploaded_file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                file_extension = os.path.splitext(uploaded_file.filename)[1].lower()
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(uploaded_file.filename))
                uploaded_file.save(file_path)

                if not request.files['uploaded-file']:
                # The file was not submitted
                    return ''
                
                session['uploaded_file_path'] = file_path
                if file_extension in ('.jpg', '.jpeg', '.png', '.gif'):
                    return render_template('index.html')
                                      
    return render_template('index.html')

@app.route('/downloadFile', methods=['POST'])
def download_image():
    if 'image-url' in request.form:
        image_url = request.form['image-url']
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            url_file = Image.open(response.raw)
            # Save the image to a file
            image_name = secure_filename(image_url.split('/')[-1])
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
            url_file.save(image_path)

            session['url_file_path'] = image_path

        return render_template('index.html')

    return render_template('index.html')
    
# Define route for displaying image
@app.route('/show_media')
def displayMedia():
    file_path = session.get('uploaded_file_path', None)
    image_path = session.get('url_file_path', None)
    media_path = file_path or image_path

    return render_template('index.html', media_path=media_path)

# Define route for object detection
@app.route('/detect_object')
def detectObject():
    uploaded_file_path = session.get('uploaded_file_path', None)
    url_file_path = session.get('url_file_path', None)
    media_image = None
    annotated_path = None

    if uploaded_file_path:
        detections = perform_inference(uploaded_file_path)
        media_image = cv2.imread(uploaded_file_path)

    elif url_file_path:
        detections = perform_inference(url_file_path)
        media_image = cv2.imread(url_file_path)

    if media_image is not None:
        annotated_media = visualize_detections(media_image, detections)

        # Get the original image extension
        _, image_extension = os.path.splitext(uploaded_file_path or url_file_path)
        image_extension = image_extension.lower()

        # Create a temporary path for the annotated image with the same format
        annotated_path = os.path.join(app.config['UPLOAD_FOLDER'], f'annotated{image_extension}')
        cv2.imwrite(annotated_path, annotated_media)


    return render_template('index.html', media_path=annotated_path)


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

if __name__ == '__main__':
    app.run(debug=True)