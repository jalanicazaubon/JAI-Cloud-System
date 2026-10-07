import boto3
from config import AWS_REGION, DYNAMODB_TABLE_NAME

s3 = boto3.client("s3", region_name=AWS_REGION)
textract = boto3.client("textract", region_name=AWS_REGION)
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
db_table = dynamodb.Table(DYNAMODB_TABLE_NAME)