from flask import Blueprint, request, jsonify, Response
from services.task_services import (
    create_task, 
    get_all_tasks, 
    get_task_by_id,
    update_task, 
    delete_task
)
from services.command_service import interpret_command_with_bedrock
from services.voice_service import transcribe_audio
from services.aws_clients import polly

task_routes = Blueprint("task_routes", __name__)

@task_routes.route("/tasks", methods=["POST"])
def create_task_route():
    data = request.get_json()
    result, status_code = create_task(data)
    return jsonify(result), status_code

@task_routes.route("/tasks", methods=["GET"])
def get_tasks_route():
    result, status_code = get_all_tasks()
    return jsonify(result), status_code

@task_routes.route("/tasks/<task_id>", methods=["GET"])
def get_task_route(task_id):
    result, status_code = get_task_by_id(task_id)
    return jsonify(result), status_code

@task_routes.route("/tasks/<task_id>", methods=["PUT"])
def update_task_route(task_id):
    data = request.get_json()
    result, status_code = update_task(task_id, data)
    return jsonify(result), status_code 

@task_routes.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task_route(task_id):
    result, status_code = delete_task(task_id)
    return jsonify(result), status_code

@task_routes.route("/tasks/command", methods=["POST"])
def commands_route():
    result = request.get_json()
    return jsonify(interpret_command_with_bedrock(result["command"])), 200

@task_routes.route("/tasks/voice", methods=["POST"])
def voice_route():
    file = request.files["file"]
    command = transcribe_audio(file.stream, file.filename)
    result = interpret_command_with_bedrock(command)
    result["command"] = command
    return jsonify(result), 200

@task_routes.route("/speech", methods=["POST"])
def speech_route():
    text = request.get_json()["text"]
    audio = polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId="Amy")
    return Response(audio["AudioStream"].read(), mimetype="audio/mpeg")