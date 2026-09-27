from app.question_parser import QuestionParser
from app.response_builder import ResponseBuilder


class ChatService:

    def __init__(self, jenkins_client):

        self.jenkins = jenkins_client
        self.parser = QuestionParser()
        self.response_builder = ResponseBuilder()

    def answer(self, question: str):

        if not question or not question.strip():
            return {
                "success": False,
                "answer": "Please enter a question."
            }

        parsed = self.parser.parse(question)

        intent = parsed["intent"]
        job_name = parsed["job_name"]

        try:

            # -------------------------
            # LIST JOBS
            # -------------------------

            if intent == "list_jobs":

                data = self.jenkins.get_jobs()

                answer = (
                    self.response_builder
                    .build_jobs_response(data)
                )

                return self._success(
                    answer,
                    parsed
                )

            # -------------------------
            # JOB STATUS
            # -------------------------

            if intent == "status":

                if not job_name:
                    return self._missing_job_response()

                data = self.jenkins.get_job_status(
                    job_name
                )

                answer = (
                    self.response_builder
                    .build_status_response(data)
                )

                return self._success(
                    answer,
                    parsed
                )

            # -------------------------
            # LATEST BUILD
            # -------------------------

            if intent == "latest_build":

                if not job_name:
                    return self._missing_job_response()

                build = self.jenkins.get_latest_build(
                    job_name
                )

                answer = (
                    self.response_builder
                    .build_latest_build_response(build)
                )

                return self._success(
                    answer,
                    parsed
                )

            # -------------------------
            # LOGS
            # -------------------------

            if intent == "logs":

                if not job_name:
                    return self._missing_job_response()

                build = self.jenkins.get_latest_build(
                    job_name
                )

                if not build:
                    return self._success(
                        "This job does not have any builds yet.",
                        parsed
                    )

                build_number = build.get("number")

                logs = self.jenkins.get_console_log(
                    job_name,
                    build_number
                )

                answer = (
                    self.response_builder
                    .build_logs_response(
                        job_name,
                        build_number,
                        logs
                    )
                )

                return self._success(
                    answer,
                    parsed
                )

            # -------------------------
            # FAILURE REASON
            # -------------------------

            if intent == "failure_reason":

                if not job_name:
                    return self._missing_job_response()

                build = self.jenkins.get_latest_build(
                    job_name
                )

                if not build:
                    return self._success(
                        "This job does not have any builds yet.",
                        parsed
                    )

                build_number = build.get("number")

                logs = self.jenkins.get_console_log(
                    job_name,
                    build_number
                )

                answer = (
                    self.response_builder
                    .build_failure_response(
                        job_name,
                        build,
                        logs
                    )
                )

                return self._success(
                    answer,
                    parsed
                )

            # -------------------------
            # BUILD HISTORY
            # -------------------------

            if intent == "build_history":

                if not job_name:
                    return self._missing_job_response()

                data = self.jenkins.get_builds(
                    job_name
                )

                builds = data.get("builds", [])

                answer = (
                    self.response_builder
                    .build_history_response(builds)
                )

                return self._success(
                    answer,
                    parsed
                )

            # -------------------------
            # UNKNOWN QUESTION
            # -------------------------

            return self._success(
                self.response_builder
                .build_unknown_response(),
                parsed
            )

        except Exception as ex:

            return {
                "success": False,
                "answer": (
                    "I couldn't retrieve the requested "
                    f"Jenkins information.\n\n"
                    f"Error: {str(ex)}"
                ),
                "intent": intent,
                "job_name": job_name
            }

    def _success(self, answer, parsed):

        return {
            "success": True,
            "answer": answer,
            "intent": parsed["intent"],
            "job_name": parsed["job_name"]
        }

    def _missing_job_response(self):

        return {
            "success": False,
            "answer": (
                "Please specify the Jenkins job name.\n\n"
                "Example:\n"
                "\"What is the status of ChatOps-Test-Job?\""
            )
        }
