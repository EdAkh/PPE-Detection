#Import necessary libraries
import torch
from super_gradients.training import models
import supervision as sv

#Define the architecture of the pre-trained model and the available device (CPU or GPU)
model_arch = 'yolo_nas_l'
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#Define the list of classes that the model can detect
classes = ['ear protection', 'hard hat', 'high visibility vest', 'mask', 'no glove', 'no helmet', 'no safety boot', 'no vest', 'safety boot', 'safety glasses', 'safety gloves']

#Load the pre-trained model outside the route function to load it only once
model = models.get(model_arch, num_classes=len(classes), checkpoint_path="model_train/ckpt_best.pth")
model.to(device)
model.eval()

#Function to perform inference on an input image
def perform_inference(image):
    #Perform inference using the model's predict function
    result = model.predict(image, conf=0.5)[0]
    
    #Create a Detections object to store detection results
    detections = sv.Detections(
        xyxy=result.prediction.bboxes_xyxy,
        confidence=result.prediction.confidence,
        class_id=result.prediction.labels.astype(int)
    )
    return detections

#Function to visualize object detection results on an input image
def visualize_detections(image, detections):
    annotated_image = image.copy()

    #Create a BoxAnnotator object for drawing bounding boxes
    box_annotator = sv.BoxAnnotator()

    #Generate labels for detected objects, including class names and confidence scores
    labels = [
        f"{classes[class_id]} {confidence:.2f}"
        for class_id, confidence
        in zip(detections.class_id, detections.confidence)
    ]

    #Annotate the input image with bounding boxes and labels
    annotated_image = box_annotator.annotate(image.copy(), detections=detections, labels=labels)

    return annotated_image
