import json
import logging
import re
from pathlib import Path
from config import BEDROCK_MODEL_ID
from services.aws_clients import bedrock

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "task_extraction.txt"
PROMPT_TEMPLATE = PROMPT_PATH.read_text()


def build_prompt(words_by_day):
    ocr_text = json.dumps(words_by_day, indent=2)
    # str.replace instead of .format so the JSON braces in the prompt are left alone.
    return PROMPT_TEMPLATE.replace("{ocr_text}", ocr_text)


def _strip_code_fences(text):
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)


def structure_tasks_with_bedrock(words_by_day):
    logging.info("Structuring tasks with Bedrock")

    response = bedrock.converse(
        modelId=BEDROCK_MODEL_ID,
        messages=[{"role": "user", "content": [{"text": build_prompt(words_by_day)}]}],
        inferenceConfig={"maxTokens": 2000, "temperature": 0},
    )

    model_text = response["output"]["message"]["content"][0]["text"]
    tasks = json.loads(_strip_code_fences(model_text)).get("tasks", [])

    # Keep only well-formed tasks so bad model output never reaches DynamoDB.
    return [
        {
            "day": task["day"],
            "title": task["title"],
            "time": task.get("time") or "unscheduled",
        }
        for task in tasks
        if isinstance(task, dict) and task.get("day") and task.get("title")
    ]
