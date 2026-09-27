import re


class QuestionParser:

    def parse(self, question: str):

        original_question = question
        text = question.lower().strip()

        return {
            "intent": self._detect_intent(text),
            "job_name": self._extract_job_name(
                original_question
            ),
            "original_question": original_question
        }

    def _detect_intent(self, text: str):

        if (
            "show all jobs" in text
            or "list jobs" in text
            or "list all jobs" in text
            or "show jobs" in text
            or "what jobs" in text
            or "which jobs" in text
        ):
            return "list_jobs"

        if (
            "why did" in text
            or "why is" in text
            or "why was" in text
            or "failure reason" in text
            or "why failed" in text
        ):
            return "failure_reason"

        if (
            "logs" in text
            or "log" in text
            or "console" in text
            or "console output" in text
        ):
            return "logs"

        if (
            "latest build" in text
            or "last build" in text
            or "most recent build" in text
        ):
            return "latest_build"

        if (
            "build history" in text
            or "recent builds" in text
            or "builds" in text
        ):
            return "build_history"

        if (
            "status" in text
            or "successful" in text
            or "success" in text
            or "running" in text
            or "failed" in text
        ):
            return "status"

        return "unknown"

    def _extract_job_name(self, question: str):

        # Handles names such as:
        # ChatOps-Test-Job
        # My-Build-Job
        # TestJob123

        match = re.search(
            r"\b[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+\b",
            question
        )

        if match:
            return match.group(0)

        return None
