from datetime import datetime


class ResponseBuilder:

    def build_jobs_response(self, data):

        jobs = data.get("jobs", [])

        if not jobs:
            return "I couldn't find any Jenkins jobs."

        lines = [
            f"I found {len(jobs)} Jenkins job(s):",
            ""
        ]

        for job in jobs:
            name = job.get("name", "Unknown")
            color = job.get("color", "Unknown")

            status = self._convert_color_to_status(color)

            lines.append(
                f"• {name} — {status}"
            )

        return "\n".join(lines)

    def build_status_response(self, data):

        name = data.get("name", "Unknown")
        color = data.get("color", "Unknown")
        status = self._convert_color_to_status(color)

        last_build = data.get("lastBuild")
        last_successful = data.get("lastSuccessfulBuild")
        last_failed = data.get("lastFailedBuild")

        lines = [
            f"Jenkins Job: {name}",
            f"Status: {status}"
        ]

        if last_build:
            lines.append(
                f"Latest build: #{last_build.get('number')}"
            )

        if last_successful:
            lines.append(
                f"Last successful build: #{last_successful.get('number')}"
            )

        if last_failed:
            lines.append(
                f"Last failed build: #{last_failed.get('number')}"
            )

        return "\n".join(lines)

    def build_latest_build_response(self, build):

        if not build:
            return "This Jenkins job does not have any builds."

        job_name = build.get("fullDisplayName", "Unknown job")
        number = build.get("number")
        result = build.get("result")
        building = build.get("building")

        status = "RUNNING" if building else result

        timestamp = build.get("timestamp")

        if timestamp:
            date = datetime.fromtimestamp(
                timestamp / 1000
            ).strftime("%Y-%m-%d %H:%M:%S")
        else:
            date = "Unknown"

        return (
            f"Job: {job_name}\n"
            f"Build: #{number}\n"
            f"Status: {status}\n"
            f"Started: {date}"
        )

    def build_logs_response(
        self,
        job_name,
        build_number,
        logs
    ):

        if not logs:
            return (
                f"No console logs were found for "
                f"{job_name} build #{build_number}."
            )

        # Keep response manageable
        max_lines = 30

        log_lines = logs.splitlines()

        if len(log_lines) > max_lines:
            log_lines = log_lines[-max_lines:]

            header = (
                f"Last {max_lines} lines from "
                f"{job_name} build #{build_number}:\n\n"
            )
        else:
            header = (
                f"Console output for "
                f"{job_name} build #{build_number}:\n\n"
            )

        return header + "\n".join(log_lines)

    def build_failure_response(
        self,
        job_name,
        build,
        logs
    ):

        if not build:
            return (
                f"I couldn't find a build for "
                f"{job_name}."
            )

        build_number = build.get("number")
        result = build.get("result")

        if result != "FAILURE":
            return (
                f"{job_name} latest build "
                f"#{build_number} is not marked as FAILURE.\n"
                f"Current result: {result}"
            )

        error_lines = self._find_error_lines(logs)

        response = (
            f"{job_name} build #{build_number} failed.\n"
        )

        if error_lines:
            response += (
                "\nPossible error details:\n"
                + "\n".join(
                    f"• {line}"
                    for line in error_lines
                )
            )
        else:
            response += (
                "\nI couldn't identify a specific error "
                "from the last console output."
            )

        return response

    def build_history_response(self, builds):

        if not builds:
            return "No build history was found."

        lines = ["Recent builds:", ""]

        for build in builds:

            number = build.get("number")
            result = build.get("result")

            if result is None:
                result = "RUNNING"

            timestamp = build.get("timestamp")

            if timestamp:
                date = datetime.fromtimestamp(
                    timestamp / 1000
                ).strftime("%Y-%m-%d %H:%M")
            else:
                date = "Unknown"

            lines.append(
                f"• Build #{number} — {result} — {date}"
            )

        return "\n".join(lines)

    def build_unknown_response(self):

        return (
            "I can currently answer questions about Jenkins jobs, "
            "build status, latest builds, build history, and console logs.\n\n"
            "Examples:\n"
            "• Show all Jenkins jobs\n"
            "• What is the status of ChatOps-Test-Job?\n"
            "• What is the latest build of ChatOps-Test-Job?\n"
            "• Show logs for ChatOps-Test-Job\n"
            "• Why did ChatOps-Test-Job fail?"
        )

    def _convert_color_to_status(self, color):

        if not color:
            return "UNKNOWN"

        mapping = {
            "blue": "SUCCESS",
            "red": "FAILURE",
            "yellow": "UNSTABLE",
            "grey": "NOT_BUILT",
            "disabled": "DISABLED",
            "aborted": "ABORTED",
            "blue_anime": "RUNNING",
            "red_anime": "RUNNING",
            "yellow_anime": "RUNNING",
            "grey_anime": "RUNNING",
        }

        return mapping.get(
            color.lower(),
            color.upper()
        )

    def _find_error_lines(self, logs):

        if not logs:
            return []

        keywords = [
            "error",
            "exception",
            "failed",
            "failure",
            "timeout",
            "fatal",
            "cannot",
            "unable"
        ]

        result = []

        for line in logs.splitlines():

            line_lower = line.lower()

            if any(
                keyword in line_lower
                for keyword in keywords
            ):
                cleaned = line.strip()

                if cleaned and cleaned not in result:
                    result.append(cleaned)

            if len(result) >= 5:
                break

        return result
