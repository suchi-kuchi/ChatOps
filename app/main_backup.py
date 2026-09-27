from app.jenkins_client import JenkinsClient
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()


app = FastAPI(
    title="ChatOps Jenkins Service",
    version="1.0.0"
)


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


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
