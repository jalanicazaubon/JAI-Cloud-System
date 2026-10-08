import json
from pathlib import Path 
from config import BEDROCK_MODEL_ID
from services.aws_clients import bedrock
from services.task_services import get_all_tasks
from services.task_extraction_service import _strip_code_fences

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "task_command.txt"
PROMPT_TEMPLATE = PROMPT_PATH.read_text()

def build_prompt(command):
    tasks, _ = get_all_tasks()

    return PROMPT_TEMPLATE.replace("{tasks}", json.dumps(tasks)).replace("{command}", command)

def interpret_command_with_bedrock(command):
    response = bedrock.converse(
        modelId=BEDROCK_MODEL_ID, 
        messages=[{"role": "user", "content": [{"text": build_prompt(command)}]}], 
        inferenceConfig={"maxTokens": 1000, "temperature": 0},
    )

    model_text = response["output"]["message"]["content"][0]["text"]
    return json.loads(_strip_code_fences(model_text))