import os
import requests
from dotenv import load_dotenv

load_dotenv()


class JenkinsClient:

    def __init__(self):
        self.base_url = os.getenv("JENKINS_URL", "").rstrip("/")
        self.username = os.getenv("JENKINS_USERNAME")
        self.token = os.getenv("JENKINS_TOKEN")

        if not self.base_url:
            raise ValueError("JENKINS_URL is not configured")

        if not self.username:
            raise ValueError("JENKINS_USERNAME is not configured")

        if not self.token:
            raise ValueError("JENKINS_TOKEN is not configured")

        self.session = requests.Session()
        self.session.auth = (
            self.username,
            self.token
        )

    def _get(self, endpoint: str):

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        response = self.session.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        return response

    def get_jobs(self):

        response = self._get(
            "/api/json?tree=jobs[name,url,color]"
        )

        return response.json()

    def get_job(self, job_name: str):

        response = self._get(
            f"/job/{job_name}/api/json"
        )

        return response.json()

    def get_job_status(self, job_name: str):

        job = self.get_job(job_name)

        return {
            "name": job.get("name"),
            "url": job.get("url"),
            "color": job.get("color"),
            "buildable": job.get("buildable"),
            "lastBuild": job.get("lastBuild"),
            "lastSuccessfulBuild": job.get(
                "lastSuccessfulBuild"
            ),
            "lastFailedBuild": job.get(
                "lastFailedBuild"
            )
        }

    def get_latest_build(self, job_name: str):

        job = self.get_job(job_name)

        latest_build = job.get("lastBuild")

        if not latest_build:
            return None

        build_number = latest_build.get("number")

        return self.get_build(
            job_name,
            build_number
        )

    def get_build(
        self,
        job_name: str,
        build_number: int
    ):

        response = self._get(
            f"/job/{job_name}/{build_number}/api/json"
        )

        return response.json()

    def get_console_log(
        self,
        job_name: str,
        build_number: int
    ):

        response = self._get(
            f"/job/{job_name}/{build_number}/consoleText"
        )

        return response.text

    def get_builds(
        self,
        job_name: str,
        limit: int = 10
    ):

        response = self._get(
            f"/job/{job_name}/api/json"
            f"?tree=builds[number,result,timestamp,duration]"
        )

        data = response.json()

        builds = data.get("builds", [])

        return {
            "builds": builds[:limit]
        }
    # def get_builds(
    #     self,
    #     job_name: str,
    #     limit: int = 10
    # ):

    #     response = self._get(
    #         f"/job/{job_name}/api/json"
    #         f"?tree=builds[number,result,timestamp,duration]"
    #         f"[0:{limit}]"
    #     )

    #     return response.json()
