import os
import cv2
from flask import Flask, render_template, request, Response
import requests
from ppedetectionmodel import perform_inference, visualize_detections
from data_storing import create_database, store_image, store_annotated_image
from PIL import Image
from io import BytesIO
from werkzeug.utils import secure_filename
import sqlite3
from fetchimage import fetch_image

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
        return Response(annotated_image_data, mimetype='image/jpeg')

    except Exception as e:
        return str(e), 500

# Define route for object detection
@app.route('/detect_object', methods=['POST'])
def detectObject():
    #confidence_threshold = request.form.get('confidence', '0.5')  # Default to 0.5 if 'confidence' is not provided
    #confidence_threshold = float(confidence_threshold)    
    image = None
    annotated_image_name = None
    annotated_image_path = None

    image_name, image_data = fetch_image()

    temp_directory = 'temp_file' # Define a temporary path

    image_path = os.path.join('app', temp_directory, image_name)

    with open(image_path, 'wb') as file:
        file.write(image_data)
    
    detections = perform_inference(image_path)
    image = cv2.imread(image_path)
        
    if image is not None:
        annotated_image = visualize_detections(image, detections)

        # Get the original image extension
        _, image_extension = os.path.splitext(image_name)
        image_extension = image_extension.lower()

        original_file_name = os.path.basename(image_name)
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