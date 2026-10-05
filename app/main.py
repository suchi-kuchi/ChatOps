import asyncio
import uvicorn

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.jenkins_client import JenkinsClient
from app.chat_service import ChatService
from app.teams.teams_bot import create_teams_app


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


# ==================================================
# MICROSOFT TEAMS INTEGRATION
# ==================================================

teams_app = create_teams_app(
    app,
    chat_service
)


# ==================================================
# START SERVER
# ==================================================

async def main():

    await teams_app.initialize()

    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=3978
    )

    server = uvicorn.Server(
        config
    )

    await server.serve()


if __name__ == "__main__":

    asyncio.run(main())
# ==================================================
# MICROSOFT TEAMS INTEGRATION
# ==================================================


# teams_adapter = FastAPIAdapter(
#     app=app
# )

# teams_app = App(
#     http_server_adapter=teams_adapter
# )


# @teams_app.on_message
# async def handle_teams_message(ctx):

#     question = ctx.activity.text.strip()

#     if not question:

#         await ctx.send(
#             "Please enter a Jenkins question."
#         )

#         return

#     result = await asyncio.to_thread(
#         chat_service.answer,
#         question
#     )

#     await ctx.send(
#         str(result)
#     )


# # ==================================================
# # START SERVER
# # ==================================================

# async def main():

#     await teams_app.initialize()

#     config = uvicorn.Config(
#         app=app,
#         host="0.0.0.0",
#         port=3978
#     )

#     server = uvicorn.Server(
#         config
#     )

#     await server.serve()


# if __name__ == "__main__":

#     asyncio.run(main())
