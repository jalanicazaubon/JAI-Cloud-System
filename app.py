from flask import Flask, jsonify, request
import uuid
import logging
import boto3 
from dotenv import load_dotenv
import os
# from boto3.exceptions import ClientError

load_dotenv()

app = Flask(__name__)

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_DEFAULT_REGION")
dynamodb_table_name = os.getenv("DYNAMODB_TABLE_NAME")

dynamo_db = boto3.resource("dynamodb", region_name=aws_region)
table = dynamo_db.Table(dynamodb_table_name)

@app.route('/')
def index():
    return jsonify({"message": "JAI API SERVER IS RUNNING"})

@app.route('/tasks', methods=['POST'])
def create_taks():
    logging.info("Creating task")
    try: 
        data = request.get_json()

        if not data or "title" not in data:
            return({"error": "title is required"}), 400

        task = {
            "task_id": str(uuid.uuid4()),
            "title": data.get('title'),
            "time": data.get('time'),
            "priority": data.get('priority', 'medium'),
        }

        table.put_item(Item=task)
        return jsonify({"message": "Task created successfully", "task": task}), 201
    
    except Exception as e: 
        return jsonify({"error": str(e)}), 500

@app.route('/tasks', methods=['GET'])
def get_tasks():
    logging.info("Getting tasks")
    try: 
        response = table.scan()
        tasks = response.get("Items", [])
        return jsonify({"Tasks": tasks}), 200

    except Exception as e: 
        return jsonify({"error": str(e)}), 500


@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id): 
    logging.info(f"Getting task {task_id}")
    try:
        response = table.get_item(Key={"task_id": task_id})
        task = response.get("Item")

        if not task:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"Task": task}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    logging.info("Health check")
    # TODO: Add ECS 
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True)