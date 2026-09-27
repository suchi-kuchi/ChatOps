from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.jenkins_client import JenkinsClient
from app.chat_service import ChatService


app = FastAPI(
    title="Jenkins ChatOps",
    description="Chat service for Jenkins",
    version="1.0.0"
)


# -------------------------
# Services
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
# Health
# -------------------------

@app.get("/health")
def health():

    return {
        "status": "UP",
        "service": "Jenkins ChatOps"
    }


# -------------------------
# Chat UI
# -------------------------

@app.get("/chat")
def chat_ui():

    return FileResponse(
        "app/static/index.html"
    )


# -------------------------
# Chat API
# -------------------------

@app.post("/chat")
def chat(
    request: ChatRequest
):

    return chat_service.answer(
        request.question
    )


# -------------------------
# Jenkins Jobs
# -------------------------

@app.get("/jenkins/jobs")
def get_jobs():

    return (
        jenkins_client
        .get_jobs()
    )


# -------------------------
# Jenkins Job Status
# -------------------------

@app.get(
    "/jenkins/jobs/{job_name}/status"
)
def get_job_status(
    job_name: str
):

    return (
        jenkins_client
        .get_job_status(
            job_name
        )
    )
