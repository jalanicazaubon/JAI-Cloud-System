# JAI-Cloud-System

AI-powered productivity assistant that converts handwritten weekly schedules into structured tasks using Amazon Textract and Amazon Bedrock. Tasks are stored in Amazon DynamoDB, deployed with Docker to Amazon ECS Fargate, and automatically delivered as daily email briefings using EventBridge Scheduler, AWS Lambda, and Amazon SNS.

---

## Features 

- Upload handwritten weekly schedules
- OCR using Amazon Textract
- AI-powered task extraction with Amazon Bedrock
- Automatic task categorization by weekday
- Priority detection (High / Medium / Low)
- REST API for task management
- CRUD operations with DynamoDB
- Daily email briefings
- Event-driven reminders using EventBridge Scheduler
- Containerized deployment with Docker
- CI/CD pipeline using GitHub Actions
- Deployment to Amazon ECS Fargate

---

## Tech Stack 

### Frontend 
- Streamlit 

### Backend 
- Python 
- Flask 

### AWS 
- Amazon ECS Fargate
- Amazon ECR
- Amazon S3
- Amazon Textract
- Amazon Bedrock
- Amazon DynamoDB
- Amazon EventBridge Scheduler
- AWS Lambda
- Amazon SNS
- IAM
- CloudWatch

### DevOps 

- Docker 
- GitHub Actions 

---

## System Architecture 

```text
User
 │
 ▼
Streamlit
 │
 ▼
Amazon S3
 │
 ▼
Amazon Textract
 │
 ▼
Amazon Bedrock
 │
 ▼
Flask API (Docker • ECS)
 │
 ▼
Amazon DynamoDB

Daily @ 7:00 AM
EventBridge Scheduler
        │
        ▼
    AWS Lambda
        │
        ▼
    Amazon SNS
        │
        ▼
   📧 Email Briefing

GitHub → GitHub Actions → Docker → Amazon ECR → Amazon ECS
```

---

## Running Locally 

```bash
git clone https://github.com/<your-username>/JAI-Cloud-System.git

cd JAI-Cloud-System

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

flask --app app run
```

```bash
streamlit run jai_ui.py
```

or 

```bash
docker build -t jai-backend .

docker run \
-p 5000:5000 \
--env-file .env \
jai-backend
```

---

## Demo 

[![JAI Cloud System Demo](screenshots/demo-thumbnail.png)](https://youtu.be/3utdQs1058I)





