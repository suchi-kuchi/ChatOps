import re


class QuestionParser:

    def parse(self, question: str):

        original_question = question
        question = question.lower().strip()

        intent = self._detect_intent(question)
        job_name = self._extract_job_name(original_question)

        return {
            "intent": intent,
            "job_name": job_name,
            "original_question": original_question
        }

    def _detect_intent(self, question: str):

        # Show all jobs
        if (
            "show all jobs" in question
            or "list jobs" in question
            or "what jobs" in question
            or "which jobs" in question
        ):
            return "list_jobs"

        # Failure reason / logs
        if (
            "why did" in question
            or "why is" in question
            or "why was" in question
            or "failure reason" in question
            or "failed" in question and "why" in question
        ):
            return "failure_reason"

        if (
            "logs" in question
            or "console" in question
            or "console output" in question
        ):
            return "logs"

        # Latest build
        if (
            "latest build" in question
            or "last build" in question
            or "most recent build" in question
        ):
            return "latest_build"

        # Build history
        if (
            "build history" in question
            or "recent builds" in question
            or "builds" in question
        ):
            return "build_history"

        # Status
        if (
            "status" in question
            or "successful" in question
            or "success" in question
            or "running" in question
            or "failed" in question
        ):
            return "status"

        return "unknown"

    def _extract_job_name(self, question: str):

        # First look for a known-looking Jenkins job name.
        # Example: ChatOps-Test-Job
        match = re.search(
            r"\b[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+\b",
            question
        )

        if match:
            return match.group(0)

        return None
