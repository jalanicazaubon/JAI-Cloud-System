import logging
import uuid
from botocore.exceptions import ClientError
from services.aws_clients import db_table

def create_task(data):
    logging.info("Creating task")

    try:
        if not data:
            return {"error": "Request body is required"}, 400

        if "title" not in data:
            return {"error": "title is required"}, 400

        if "day" not in data:
            return {"error": "day is required"}, 400

        task = {
            "task_id": str(uuid.uuid4()),
            "day": data.get("day"),
            "title": data.get("title"),
            "time": data.get("time", "unscheduled"),
            "completed": data.get("completed", False)
        }

        db_table.put_item(Item=task)

        return task, 201

    except ClientError as e:
        return {
            "error": "Unable to create task",
            "details": e.response["Error"]["Message"],
        }, 500


def get_all_tasks():
    logging.info("Getting tasks")

    try:
        response = db_table.scan()
        return response.get("Items", []), 200

    except ClientError as e:
        return {
            "error": "Unable to get tasks",
            "details": e.response["Error"]["Message"],
        }, 500


def get_task_by_id(task_id):
    logging.info(f"Getting task {task_id}")

    try:
        if not task_id:
            return {"error": "Task ID is required"}, 400

        response = db_table.get_item(
            Key={"task_id": task_id}
        )

        task = response.get("Item")

        if not task:
            return {"error": "Task not found"}, 404

        return task, 200

    except ClientError as e:
        return {
            "error": "Unable to get task",
            "details": e.response["Error"]["Message"],
        }, 500


def update_task(task_id, data):
    logging.info(f"Updating task {task_id}")

    try:
        if not task_id:
            return {"error": "Task ID is required"}, 400

        if not data:
            return {"error": "Request body is required"}, 400

        fields = ["day", "title", "time", "completed"]

        updates = []
        expression_values = {}
        expression_names = {}

        for field in fields:
            if field in data:
                updates.append(f"#{field} = :{field}")
                expression_names[f"#{field}"] = field
                expression_values[f":{field}"] = data[field]

        if not updates:
            return {"error": "No valid fields provided"}, 400

        response = db_table.update_item(
            Key={"task_id": task_id},
            UpdateExpression="SET " + ", ".join(updates),
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values,
            ReturnValues="ALL_NEW",
        )

        return response["Attributes"], 200

    except ClientError as e:
        return {
            "error": "Unable to update task",
            "details": e.response["Error"]["Message"],
        }, 500


def delete_task(task_id):
    logging.info(f"Deleting task {task_id}")

    try:
        if not task_id:
            return {"error": "Task ID is required"}, 400

        response = db_table.delete_item(
            Key={"task_id": task_id},
            ReturnValues="ALL_OLD",
        )

        if "Attributes" not in response:
            return {"error": "Task not found"}, 404

        return {"message": "Task deleted successfully"}, 200

    except ClientError as e:
        return {
            "error": "Unable to delete task",
            "details": e.response["Error"]["Message"],
        }, 500