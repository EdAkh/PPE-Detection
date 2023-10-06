#Import necessary libraries
import os
import cv2
from flask import Flask, render_template, request, Response
import requests
from ppedetectionmodel import perform_inference, visualize_detections
from data_storing import create_database, store_image, store_annotated_image
from io import BytesIO
from werkzeug.utils import secure_filename
import sqlite3
from fetchimage import fetch_image
import signal

#Define upload and temporary directories
UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
TEMP_DIRECTORY = os.path.join('app', 'temp_file')

#Create a Flask application
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Function to clean temporary files when the application is terminated
def clean_temp_folder():
    for file in os.listdir(TEMP_DIRECTORY):
        os.remove(os.path.join(TEMP_DIRECTORY, file))

#Register a signal handler to clean temporary files on termination
signal.signal(signal.SIGTERM, clean_temp_folder)

#Define the default route
@app.route('/')
def index():
    return render_template('index.html')

#Route to handle file uploads
@app.route('/uploadFile', methods=['POST', 'GET'])
def uploadFile():
    if request.method == 'POST':
        if 'uploaded-file' in request.files:
            uploaded_file = request.files['uploaded-file']
            if uploaded_file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                #Get the image data and file extension
                image_name = uploaded_file.filename
                image_data = uploaded_file.read()
                file_extension = os.path.splitext(image_name)[1].lower()

                #Store the image data in the database
                store_image(image_name, image_data)

                if file_extension in ('.jpg', '.jpeg', '.png', '.gif'):
                    return render_template('index.html')

    return render_template('index.html')

#Route to handle downloading images from URLs
@app.route('/downloadFile', methods=['POST'])
def download_image():
    if 'image-url' in request.form:
        image_url = request.form['image-url']
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            image_data = BytesIO(response.content).read()
            image_name = secure_filename(image_url.split('/')[-1])
            file_extension = os.path.splitext(image_name)[1].lower()

            #Store the downloaded image data in the database
            store_image(image_name, image_data)

            if file_extension in ('.jpg', '.jpeg', '.png', '.gif'):
                return render_template('index.html')

    return render_template('index.html')

#Route to display the uploaded image
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
        return Response(image_data, mimetype='image/*')
    
    except Exception as e:
        return str(e), 500

#Route to display the annotated image with object detection
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

#Route for object detection
@app.route('/detect_object', methods=['POST'])
def detectObject():
    image = None
    annotated_image_name = None
    annotated_image_path = None
    image_name, image_data = fetch_image()

    image_path = os.path.join(TEMP_DIRECTORY, image_name)

    with open(image_path, 'wb') as file:
        file.write(image_data)

    #Perform object detection on the uploaded image
    detections = perform_inference(image_path)
    image = cv2.imread(image_path)
        
    if image is not None:
        annotated_image = visualize_detections(image, detections)

        #Get the original image extension
        _, image_extension = os.path.splitext(image_name)
        image_extension = image_extension.lower()

        original_file_name = os.path.basename(image_name)
        annotated_image_name = 'annotated_' + original_file_name + image_extension
        #Create a temporary path for the annotated image with the same format
        annotated_image_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_image_name)
        cv2.imwrite(annotated_image_path, annotated_image)

        #Store the annotated image in the database
        with open(annotated_image_path, 'rb') as annotated_image_file:
            annotated_image_data = annotated_image_file.read()
            store_annotated_image(annotated_image_name, annotated_image_data)

    return render_template('index.html')

#Add headers to prevent caching
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

#Create the database and start the Flask application
if __name__ == '__main__':
    create_database()
    app.run(debug=True)
