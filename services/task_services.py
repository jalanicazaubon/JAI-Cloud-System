from flask import jsonify, request
import uuid
import logging
import boto3 
from dotenv import load_dotenv
import os
# from boto3.exceptions import ClientError

load_dotenv()

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_DEFAULT_REGION")
dynamodb_table_name = os.getenv("DYNAMODB_TABLE_NAME")

dynamo_db = boto3.resource("dynamodb", region_name=aws_region)
table = dynamo_db.Table(dynamodb_table_name)

def create_task():
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

def get_all_tasks():
    logging.info("Getting tasks")
    try: 
        response = table.scan()
        tasks = response.get("Items", [])
        return jsonify({"Tasks": tasks}), 200

    except Exception as e: 
        return jsonify({"error": str(e)}), 500


def get_task_by_id(task_id): 
    logging.info(f"Getting task {task_id}")
    try:
        response = table.get_item(Key={"task_id": task_id})
        task = response.get("Item")

        if not task:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"Task": task}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def update_task(task_id):
    logging.info(f"Updating task {task_id}")
    try: 
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        update_expression = "SET "
        expression_values = {}

        fields = ["title", "time", "priority"]

        updates = []
        for field in fields: 
            if field in data: 
                updates.append(f"{field} = :{field}")
                expression_values[f":{field}"] = data[field]
        
        if not updates: 
            return jsonify({"error": "No valid fields provided"}), 400

        update_expression += ", ".join(updates)

        response = table.update_item(
            Key={"task_id": task_id}, 
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values, 
            ReturnValues="ALL_NEW"
        )

        return jsonify(response["Attributes"]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def delete_task(task_id):
    try:
        response = table.delete_item(
            Key={"task_id": task_id},
            ReturnValues="ALL_OLD"
        )

        if "Attributes" not in response:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"message": "Task deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
