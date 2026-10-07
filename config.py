import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")