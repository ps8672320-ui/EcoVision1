
from flask import Flask, render_template, request, jsonify
from waste_ai import classify_waste
from PIL import Image
import os
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


def get_disposal_advice(label):
    label = label.lower()

    if "plastic" in label:
        return "Empty and clean the item. Recycle it if accepted locally."

    elif "paper" in label or "cardboard" in label:
        return "Keep it dry and separate it for paper recycling."

    elif "glass" in label:
        return "Separate carefully. Wrap broken glass securely."

    elif "metal" in label:
        return "Separate it for appropriate metal recycling."

    elif "biological" in label or "organic" in label:
        return "Separate organic waste for composting where available."

    elif "battery" in label or "electronic" in label:
        return "Take it to an authorised battery or e-waste collection point."

    elif "clothes" in label or "shoes" in label:
        return "Consider reusing, donating, or using a textile collection service."

    elif "trash" in label or "waste" in label:
        return "Check the material and local waste disposal guidelines."

    else:
        return "Check the item's material and local waste disposal guidelines."


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_image():
    image_file = request.files.get("image")

    if not image_file or image_file.filename == "":
        return jsonify({
            "error": "Please select an image first."
        }), 400

    if not image_file.mimetype or not image_file.mimetype.startswith("image/"):
        return jsonify({
            "error": "Please upload a valid image file."
        }), 400

    try:
        image = Image.open(
            io.BytesIO(image_file.read())
        ).convert("RGB")

        result = classify_waste(image)

        label = result["label"]
        confidence = result["confidence"]
        advice = get_disposal_advice(label)

        return jsonify({
            "message": "AI analysis completed!",
            "classification": label,
            "confidence": confidence,
            "advice": advice
        })

    except Exception:
        app.logger.exception("Image analysis failed")
        return jsonify({
            "error": "Unable to analyse this image. Please try another image."
        }), 500


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "error": "Image is too large. Please upload an image under 10 MB."
    }), 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)