import logging
import uuid
from config import S3_BUCKET_NAME
from services.aws_clients import s3, textract

WEEKDAYS = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]

def upload_to_s3(file_stream, filename):
    key = f"uploads/{uuid.uuid4()}-{filename}"
    logging.info(f"Uploading schedule to s3://{S3_BUCKET_NAME}/{key}")
    s3.upload_fileobj(file_stream, S3_BUCKET_NAME, key)
    return key


def run_textract(key):
    logging.info(f"Running Textract on {key}")
    response = textract.detect_document_text(
        Document={"S3Object": {"Bucket": S3_BUCKET_NAME, "Name": key}}
    )
    return response["Blocks"]


def _center(block):
    box = block["Geometry"]["BoundingBox"]
    return box["Left"] + box["Width"] / 2, box["Top"] + box["Height"] / 2


def group_words_by_day(blocks):
    extracted_text = {day: "" for day in WEEKDAYS}

    for block in blocks:
        if block["BlockType"] != "WORD":
            continue

        x, y = _center(block)

        if x < 0.5 and 0.15 < y < 0.30:
            extracted_text["Sunday"] += block["Text"] + " "
        elif x > 0.5 and 0.15 < y < 0.30:
            extracted_text["Monday"] += block["Text"] + " "
        elif x < 0.5 and 0.35 < y < 0.50:
            extracted_text["Tuesday"] += block["Text"] + " "
        elif x > 0.5 and 0.35 < y < 0.50:
            extracted_text["Wednesday"] += block["Text"] + " "
        elif x < 0.5 and 0.55 < y < 0.70:
            extracted_text["Thursday"] += block["Text"] + " "
        elif x > 0.5 and 0.55 < y < 0.70:
            extracted_text["Friday"] += block["Text"] + " "
        elif x < 0.5 and 0.75 < y < 0.90:
            extracted_text["Saturday"] += block["Text"] + " "

    return extracted_text
