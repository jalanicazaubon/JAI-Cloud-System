import json
import logging
from botocore.exceptions import ClientError
from services.ocr_service import group_words_by_day, run_textract, upload_to_s3
from services.task_extraction_service import structure_tasks_with_bedrock


def process_schedule(file_stream, filename):
    logging.info(f"Processing schedule {filename}")

    try:
        key = upload_to_s3(file_stream, filename)
        blocks = run_textract(key)
        words_by_day = group_words_by_day(blocks)
        tasks = structure_tasks_with_bedrock(words_by_day)

        return {"tasks": tasks, "ocr": words_by_day}, 200

    except ClientError as e:
        return {
            "error": "AWS request failed",
            "details": e.response["Error"]["Message"],
        }, 502

    except json.JSONDecodeError:
        return {"error": "Bedrock returned invalid JSON"}, 502
