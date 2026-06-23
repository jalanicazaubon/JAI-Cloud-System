import streamlit as st 
import boto3 
# import requests 
import uuid
import re 

BUCKET_NAME = "jai-schedule-uploads"
API_URL = "http://127.0.0.1:5000/tasks"

s3 = boto3.client("s3", region_name="us-east-1")
textract = boto3.client("textract", region_name="us-east-1")

st.title("JAI Lite")
uploaded_file = st.file_uploader("Upload a handwritten schedule", type=["png", "jpg", "jpeg"])

def clean_line(line):
    line = line.strip()

    # Fix OCR duplicates
    line = re.sub(
        r"(\d{1,2}:\d{2})\s+\d{1,2}\s+\d{2}\s*(AM|PM|am|pm)",
        r"\1 \2",
        line
    )

    return line 

def extract_tasks(text):
    tasks = []
    lines = [clean_line(line) for line in text.split("\n") if line.strip()]
    
    for line in lines: 
        time_match = re.search(fr"(\d{1,2}:\d{2}\s?(AM|PM|am|pm)?)", line)

        time = time_match.group(1) if time_match else "unscheduled"

        title = line.replace(time, "").strip()

        task = {
            "title": title, 
            "time": time, 
            "priority": "medium"
        }
        

        tasks.append(task)

    return tasks

def generate_summary(tasks):
    return f"You have {len(tasks)} tasks today."

if uploaded_file:
    file_key = f"uploads/{uuid.uuid4()}-{uploaded_file.name}"

    s3.upload_fileobj(uploaded_file, BUCKET_NAME, file_key)

    response = textract.detect_document_text(
        Document={
            "S3Object": {
                "Bucket": BUCKET_NAME, 
                "Name": file_key 
            }
        }
    )

    extracted_text = "\n".join(
        block["Text"]
        for block in response["Blocks"]
        if block["BlockType"] == "LINE"
    )

    st.subheader("Extracted Text")
    st.text(extracted_text)

    tasks = extract_tasks(extracted_text)

    st.subheader("Detected Tasks")
    st.json(tasks)

    st.subheader("Daily Briefing")
    st.write(generate_summary(tasks))

    # if st.button("Send Tasks to Backend")
    #     for task in tasks:
    #         response = requests.post(API_URL, json=task)
    #         if response.status_code == 201:
    #             st.sucess(f"Saved: {task['title']}")
    #         else:
    #             st.error(f"Failed: {task['title']}")
    

