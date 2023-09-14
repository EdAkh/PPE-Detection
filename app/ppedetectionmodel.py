import torch
from super_gradients.training import models
import supervision as sv

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