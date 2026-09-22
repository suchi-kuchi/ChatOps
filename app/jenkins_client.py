import os
import requests
from dotenv import load_dotenv

load_dotenv()


class JenkinsClient:

    def __init__(self):
        self.base_url = os.getenv("JENKINS_URL")
        self.username = os.getenv("JENKINS_USERNAME")
        self.api_token = os.getenv("JENKINS_API_TOKEN")

        if not self.base_url:
            raise ValueError("JENKINS_URL is not configured")

        if not self.username:
            raise ValueError("JENKINS_USERNAME is not configured")

        if not self.api_token:
            raise ValueError("JENKINS_API_TOKEN is not configured")

    def _get(self, url):
        response = requests.get(
            url,
            auth=(self.username, self.api_token),
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    def get_jobs(self):
        url = f"{self.base_url}/api/json"

        return self._get(url)

    def get_job(self, job_name):
        url = f"{self.base_url}/job/{job_name}/api/json"

        return self._get(url)

    def get_last_build(self, job_name):
        url = f"{self.base_url}/job/{job_name}/lastBuild/api/json"

        return self._get(url)

    def get_console_output(self, job_name):
        url = (
            f"{self.base_url}/job/"
            f"{job_name}/lastBuild/consoleText"
        )

        response = requests.get(
            url,
            auth=(self.username, self.api_token),
            timeout=30
        )

        response.raise_for_status()

        return response.text
