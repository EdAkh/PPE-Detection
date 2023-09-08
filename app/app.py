import os
import torch
import cv2
from flask import Flask, render_template, request, session, send_file, Response
import requests
from super_gradients.training import models
import supervision as sv
from io import BytesIO
from werkzeug.utils import secure_filename
import secret
import sqlite3
import base64

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

def create_database():
    conn = sqlite3.connect('image_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT,
            image_data BLOB
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS annotated_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            annotated_image_name TEXT,
            annotated_image_data BLOB
        )
    ''')
    conn.commit()
    conn.close()

def store_image(image_name, image_data):
    conn = sqlite3.connect('image_database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO images (image_name, image_data) VALUES (?, ?)', (image_name, image_data))
    conn.commit()
    conn.close()

def store_annotated_image(annotated_image_name, annotated_image_data):
    conn = sqlite3.connect('image_database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO annotated_images (annotated_image_name, annotated_image_data) VALUES (?, ?)', (annotated_image_name, annotated_image_data))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploadFile', methods=['POST', 'GET'])
def uploadFile():
    if request.method == 'POST':
        if 'uploaded-file' in request.files:
            uploaded_file = request.files['uploaded-file']
            if uploaded_file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                image_name = uploaded_file.filename
                # Get the image data
                image_data = uploaded_file.read()
                file_extension = os.path.splitext(uploaded_file.filename)[1].lower()

                # Store the image data in the database
                store_image(image_name, image_data)

                session['uploaded_file_path'] = image_name
                if file_extension in ('.jpg', '.jpeg', '.png', '.gif'):
                    return render_template('index.html')

    return render_template('index.html')

@app.route('/downloadFile', methods=['POST'])
def download_image():
    if 'image-url' in request.form:
        image_url = request.form['image-url']
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            image_data = BytesIO(response.content).read()
            image_name = secure_filename(image_url.split('/')[-1])

            # Store the downloaded image data in the database
            store_image(image_name, image_data)

            session['url_file_path'] = image_name

        return render_template('index.html')

    return render_template('index.html')

@app.route('/display', methods=['GET'])
def displayImage():
    try:
        conn = sqlite3.connect('image_database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(id) FROM images')
        image_id = cursor.fetchone()[0]
        cursor.execute('SELECT image_data FROM images WHERE id = ?', (image_id,))
        image_data = cursor.fetchone()[0]
        conn.close()
        return Response(image_data, mimetype='image/jpeg')
    
    except Exception as e:
        return str(e), 500


@app.route('/display_detection', methods=['GET'])
def displayDetection():
    try:
        conn = sqlite3.connect('image_database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(id) FROM annotated_images')
        annotated_image_id = cursor.fetchone()[0]
        cursor.execute('SELECT annotated_image_data FROM annotated_images WHERE id = ?', (annotated_image_id,))
        annotated_image_data = cursor.fetchone()[0]
        conn.close()
        return Response(annotated_image_data, mimetype='image/*')

    except Exception as e:
        return str(e), 500

# Define route for object detection
@app.route('/detect_object', methods=['POST'])
def detectObject():
    #confidence_threshold = request.form.get('confidence', '0.5')  # Default to 0.5 if 'confidence' is not provided
    #confidence_threshold = float(confidence_threshold)    
    uploaded_file_path = session.get('uploaded_file_path', None)
    url_file_path = session.get('url_file_path', None)
    image = None
    annotated_image_name = None
    annotated_image_path = None

    if uploaded_file_path:
        detections = perform_inference(uploaded_file_path)
        image = cv2.imread(uploaded_file_path)

    elif url_file_path:
        detections = perform_inference(url_file_path)
        image = cv2.imread(url_file_path)

    if image is not None:
        annotated_image = visualize_detections(image, detections)

        # Get the original image extension
        _, image_extension = os.path.splitext(uploaded_file_path or url_file_path)
        image_extension = image_extension.lower()

        original_file_name = os.path.basename(uploaded_file_path or url_file_path)
        annotated_image_name = 'annotated_' + original_file_name + image_extension
        # Create a temporary path for the annotated image with the same format
        annotated_image_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_image_name)
        cv2.imwrite(annotated_image_path, annotated_image)

        # Store the annotated image in the database
        with open(annotated_image_path, 'rb') as annotated_image_file:
            annotated_image_data = annotated_image_file.read()
            store_annotated_image(annotated_image_name, annotated_image_data)


    return render_template('index.html')


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

if __name__ == '__main__':
    create_database()
    app.run(debug=True)
