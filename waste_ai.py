from transformers import pipeline

print("Loading waste classification AI model... Please wait.")

classifier = pipeline(
    "image-classification",
    model="watersplash/waste-classification"
)

print("Waste classification model loaded successfully!")


def classify_waste(image):
    results = classifier(image, top_k=1)

    prediction = results[0]

    return {
        "label": prediction["label"],
        "confidence": round(prediction["score"] * 100, 2)
    }