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
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "png",
    "bmp", "tiff", "tif",
    "webp"
}

MIME_MAP = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "bmp": "image/bmp",
    "tiff": "image/tiff",
    "tif": "image/tiff",
    "webp": "image/webp"
}


# ==============================
# HELPERS
# ==============================

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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
# VERIFY & ENFORCE
# ------------------------------------------------
@app.route("/verify", methods=["POST"])
def verify_image():

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

    detection = detect_watermark(file_path)
    status = detection["status"]
    confidence = detection["confidence"]

    policy_result = enforce_policy(status, context)

    return jsonify({
        "detection_status": status,
        "confidence": confidence,
        "context": context,
        "decision": policy_result["decision"],
        "reason": policy_result["reason"]
    }), 200


# ------------------------------------------------
# EMBED / SIMULATED AI GENERATION
# ------------------------------------------------
@app.route("/embed", methods=["POST"])
def embed_image():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported image format"}), 400

    input_ext = file.filename.rsplit(".", 1)[1].lower()
    mime_type = MIME_MAP[input_ext]

    input_filename = secure_filename(file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], input_filename)
    file.save(input_path)

    output_filename = f"signed_{uuid.uuid4().hex}.{input_ext}"
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)

    embed_watermark(input_path, output_path)

    if not os.path.exists(output_path):
        return jsonify({"error": "Failed to generate signed image"}), 500

    return send_file(
        output_path,
        mimetype=mime_type,
        as_attachment=True,
        download_name="ai_signed_image." + input_ext
    )


# ==============================
# RUN SERVER
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


