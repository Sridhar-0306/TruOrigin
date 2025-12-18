from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid

from detect import detect_watermark
from policy import enforce_policy
from embed import embed_watermark

# ==============================
# APP CONFIG
# ==============================

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"

# Supported image formats
ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "png",
    "bmp", "tiff", "tif",
    "webp"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==============================
# HELPERS
# ==============================

def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ==============================
# ROUTES
# ==============================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "AI Auth MVP API is running",
        "endpoints": ["/verify", "/embed"]
    })


# ------------------------------------------------
# VERIFY & ENFORCE (existing functionality)
# ------------------------------------------------
@app.route("/verify", methods=["POST"])
def verify_image():
    """
    Upload image → detect watermark → enforce policy
    """

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    context = request.form.get("context", "").lower()

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported image format"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # 1️⃣ Detect watermark
    detection = detect_watermark(file_path)
    status = detection["status"]
    confidence = detection["confidence"]

    # 2️⃣ Enforce policy
    policy_result = enforce_policy(status, context)

    return jsonify({
        "detection_status": status,
        "confidence": confidence,
        "context": context,
        "decision": policy_result["decision"],
        "reason": policy_result["reason"]
    }), 200


# ------------------------------------------------
# EMBED / SIMULATE AI GENERATION (NEW)
# ------------------------------------------------
@app.route("/embed", methods=["POST"])
def embed_image():
    """
    Upload image → embed watermark → return AI-signed image
    """

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported image format"}), 400

    # Save input image
    input_ext = file.filename.rsplit(".", 1)[1].lower()
    input_name = secure_filename(file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], input_name)
    file.save(input_path)

    # Output signed image (preserve format)
    output_filename = f"signed_{uuid.uuid4().hex}.{input_ext}"
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)

    embed_watermark(input_path, output_path)

    return send_file(
        output_path,
        as_attachment=True,
        mimetype=f"image/{input_ext}"
    )


# ==============================
# RUN SERVER
# ==============================

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

