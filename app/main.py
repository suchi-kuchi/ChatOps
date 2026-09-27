from fastapi import FastAPI
from pydantic import BaseModel

from app.jenkins_client import JenkinsClient
from app.chat_service import ChatService


app = FastAPI(
    title="ChatOps Jenkins Service",
    description="Chat service for Jenkins operations",
    version="1.0.0"
)


# -------------------------
# Initialize services
# -------------------------

jenkins_client = JenkinsClient()

chat_service = ChatService(
    jenkins_client
)


# -------------------------
# Request model
# -------------------------

class ChatRequest(BaseModel):
    question: str


# -------------------------
# Health check
# -------------------------

@app.get("/health")
def health():

    return {
        "status": "UP",
        "service": "ChatOps Jenkins Service"
    }


# -------------------------
# Jenkins jobs
# -------------------------

@app.get("/jenkins/jobs")
def get_jobs():

    return jenkins_client.get_jobs()


# -------------------------
# Jenkins job status
# -------------------------

@app.get("/jenkins/jobs/{job_name}/status")
def get_job_status(job_name: str):

    return jenkins_client.get_job_status(
        job_name
    )


# -------------------------
# Chat endpoint
# -------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    return chat_service.answer(
        request.question
    )
