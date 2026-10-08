import time
import uuid
import requests
from config import S3_BUCKET_NAME
from services.aws_clients import transcribe
from services.ocr_service import upload_to_s3

def transcribe_audio(file_stream, filename):
    key = upload_to_s3(file_stream, filename)
    job_name = str(uuid.uuid4())

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": f"s3://{S3_BUCKET_NAME}/{key}"},
        MediaFormat="wav",
        LanguageCode="en-US",
    )

    while True:
        job = transcribe.get_transcription_job(TranscriptionJobName=job_name)["TranscriptionJob"]
        if job["TranscriptionJobStatus"] in ("COMPLETED", "FAILED"):    
            break
        time.sleep(1)

    if job["TranscriptionJobStatus"] == "FAILED":
        return ""

    transcript = requests.get(job["Transcript"]["TranscriptFileUri"]).json()
    return transcript["results"]["transcripts"][0]["transcript"]