from flask import Blueprint, jsonify, request
from services.schedule_service import process_schedule

schedule_routes = Blueprint("schedule_routes", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


@schedule_routes.route("/schedules/upload", methods=["POST"])
def upload_schedule_route():
    file = request.files.get("file")

    if not file or not file.filename:
        return jsonify({"error": "No file uploaded"}), 400

    extension = file.filename.rsplit(".", 1)[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "File must be PNG, JPG, or JPEG"}), 400

    result, status_code = process_schedule(file.stream, file.filename)
    return jsonify(result), status_code
