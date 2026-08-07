import json
import re
import uuid
import boto3
import requests
import streamlit as st

BUCKET_NAME = "jai-schedule-uploads"
API_URL = "http://127.0.0.1:5001/tasks"
AWS_REGION = "us-east-1"

s3 = boto3.client("s3", region_name=AWS_REGION)
textract = boto3.client("textract", region_name=AWS_REGION)
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

def structure_tasks_with_bedrock(extracted_text):
    prompt = f"""
        Convert this OCR output from a handwritten weekly schedule into structured tasks.

        Rules:
        - Weekday headings are Sunday through Saturday.
        - Each task belongs to the most recent weekday heading.
        - 0/O = high priority.
        - - = medium priority.
        - X/x = low priority.
        - Extract times when present.
        - If no time exists, use "unscheduled".
        - Correct obvious OCR mistakes caused by handwriting.
        - Do not invent tasks.
        - Return only valid JSON.

        Required format:

        {{
        "tasks": [
            {{
            "day": "Monday",
            "title": "Task name",
            "time": "9:00 AM",
            "priority": "high"
            }}
        ]
        }}

        OCR:
        {extracted_text}
    """

    response = bedrock.converse(
        modelId="amazon.nova-lite-v1:0",
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        inferenceConfig={
            "maxTokens": 1000,
            "temperature": 0,
        },
    )

    model_text = response["output"]["message"]["content"][0]["text"].strip()

    model_text = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        model_text,
        flags=re.IGNORECASE,
    )

    return json.loads(model_text).get("tasks", [])


def generate_summary(tasks):
    return f"You have {len(tasks)} tasks today."


st.title("JAI Lite")

uploaded_file = st.file_uploader(
    "Upload a handwritten schedule",
    type=["png", "jpg", "jpeg"],
)

if uploaded_file:
    file_key = f"uploads/{uuid.uuid4()}-{uploaded_file.name}"

    s3.upload_fileobj(
        uploaded_file,
        BUCKET_NAME,
        file_key,
    )

    textract_response = textract.detect_document_text(
        Document={
            "S3Object": {
                "Bucket": BUCKET_NAME,
                "Name": file_key,
            }
        }
    )

    extracted_text = "\n".join(
        block["Text"]
        for block in textract_response["Blocks"]
        if block["BlockType"] == "LINE"
    )

    tasks = []

    try:
        tasks = structure_tasks_with_bedrock(extracted_text)
    except Exception as e:
        st.warning(f"Bedrock could not structure the tasks. {e}")

    st.subheader("Detected Tasks")
    st.json(tasks)

    st.subheader("Daily Briefing")
    st.write(generate_summary(tasks))

    if st.button("Save Tasks"):
        for task in tasks:
            api_response = requests.post(
                API_URL,
                json=task,
            )

            if api_response.status_code == 201:
                st.success(f"Saved: {task['title']}")
            else:
                st.error(
                    f"Failed: {task['title']} | "
                    f"Status: {api_response.status_code} | "
                    f"Response: {api_response.text}"
                )