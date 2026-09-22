import asyncio
import uvicorn

from fastapi import FastAPI, HTTPException

from microsoft_teams.apps import App, FastAPIAdapter

from app.jenkins_client import JenkinsClient


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="ChatOps Jenkins Service",
    version="1.0.0"
)


# --------------------------------------------------
# Existing health endpoint
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# --------------------------------------------------
# Existing Jenkins endpoints
# --------------------------------------------------

@app.get("/jenkins/jobs")
def get_jenkins_jobs():

    try:
        jenkins = JenkinsClient()

        data = jenkins.get_jobs()

        return {
            "jobs": data.get("jobs", [])
        }

    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )


@app.get("/jenkins/jobs/{job_name}/status")
def get_job_status(job_name: str):

    try:
        jenkins = JenkinsClient()

        build = jenkins.get_last_build(job_name)

        return {
            "job": job_name,
            "build_number": build.get("number"),
            "status": build.get("result"),
            "building": build.get("building"),
            "duration_ms": build.get("duration")
        }

    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )


@app.get("/jenkins/jobs/{job_name}/logs")
def get_job_logs(job_name: str):

    try:
        jenkins = JenkinsClient()

        build = jenkins.get_last_build(job_name)

        logs = jenkins.get_console_output(job_name)

        return {
            "job": job_name,
            "build_number": build.get("number"),
            "status": build.get("result"),
            "logs": logs
        }

    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )


# --------------------------------------------------
# Teams integration
# --------------------------------------------------

teams_adapter = FastAPIAdapter(app=app)

teams_app = App(
    http_server_adapter=teams_adapter
)


# --------------------------------------------------
# Teams message handler
# --------------------------------------------------

@teams_app.on_message
async def handle_message(ctx):

    message = (ctx.activity.text or "").strip()

    print(f"Teams message received: {message}")

    await ctx.send(
        f"🤖 ChatOps received: {message}"
    )


# --------------------------------------------------
# Start application
# --------------------------------------------------

async def main():

    # Registers /api/messages
    await teams_app.initialize()

    print("ChatOps Teams Service starting...")
    print("Health: http://localhost:3978/health")
    print("Teams endpoint: http://localhost:3978/api/messages")

    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=3978
    )

    server = uvicorn.Server(config)

    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())