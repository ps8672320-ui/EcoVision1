
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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_image():

    image = request.files.get("image")

    if not image or image.filename == "":
        return jsonify({
            "error": "Please select an image."
        }), 400

    if not image.mimetype or not image.mimetype.startswith("image/"):
        return jsonify({
            "error": "Please upload an image file."
        }), 400

    try:
        img = Image.open(
            io.BytesIO(image.read())
        ).convert("RGB")

        result = classify_waste(img)

        return jsonify({
            "message": "AI analysis completed!",
            "classification": result["label"],
            "material": result["label"],
            "category": result["category"],
            "confidence": result["confidence"],
            "disposal": result["disposal"]
        })

    except Exception:
        app.logger.exception("Image classification failed")

        return jsonify({
            "error": "Could not analyse this image. Please try again."
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
