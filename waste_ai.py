
import os
import numpy as np
import onnxruntime as ort
from PIL import Image

# Load the small AI model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "wastewise-yolo.onnx")

session = ort.InferenceSession(
    MODEL_PATH,
    providers=["CPUExecutionProvider"]
)

input_name = session.get_inputs()[0].name

# Supported waste materials
CLASS_NAMES = [
    "battery",
    "biological",
    "cardboard",
    "glass",
    "metal",
    "paper",
    "plastic",
    "trash"
]

# Map materials to broad waste categories
WASTE_CATEGORIES = {
    "battery": "Hazardous Waste",
    "biological": "Biodegradable Waste",
    "cardboard": "Recyclable Waste",
    "glass": "Recyclable Waste",
    "metal": "Recyclable Waste",
    "paper": "Recyclable Waste",
    "plastic": "Recyclable Waste",
    "trash": "General Waste"
}

DISPOSAL_GUIDE = {
    "battery": "Take to an authorized battery collection point.",
    "biological": "Compost suitable organic waste.",
    "cardboard": "Keep clean and send for paper recycling.",
    "glass": "Separate and send to a glass recycling facility.",
    "metal": "Separate and send for metal recycling.",
    "paper": "Keep dry and send for paper recycling.",
    "plastic": "Check local recycling rules and separate by type.",
    "trash": "Dispose of through the general waste collection system."
}


def classify_waste(image):

    # Convert image to RGB and resize
    image = image.convert("RGB").resize((224, 224))

    # Prepare image for AI model
    image_array = np.array(
        image, dtype=np.float32
    ) / 255.0

    tensor = np.transpose(
        image_array, (2, 0, 1)
    )[np.newaxis, ...]

    # Predict waste material
    outputs = session.run(
        None,
        {input_name: tensor}
    )

    scores = outputs[0][0]

    class_id = int(np.argmax(scores))
    confidence = float(scores[class_id]) * 100

    label = CLASS_NAMES[class_id]

    return {
        "label": label.title(),
        "confidence": round(confidence, 2),
        "category": WASTE_CATEGORIES[label],
        "disposal": DISPOSAL_GUIDE[label]
    }
