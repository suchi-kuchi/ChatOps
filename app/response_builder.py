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

            name = job.get(
                "name",
                "Unknown"
            )

            color = job.get(
                "color",
                "unknown"
            )

            status = self._convert_color_to_status(
                color
            )

            lines.append(
                f"• {name} — {status}"
            )

        return "\n".join(lines)

    def build_status_response(self, data):

        name = data.get(
            "name",
            "Unknown"
        )

        color = data.get(
            "color",
            "unknown"
        )

        status = self._convert_color_to_status(
            color
        )

        latest = data.get("lastBuild")
        successful = data.get(
            "lastSuccessfulBuild"
        )
        failed = data.get(
            "lastFailedBuild"
        )

        lines = [
            f"**{name}**",
            "",
            f"Status: **{status}**"
        ]

        if latest:
            lines.append(
                f"Latest build: **#{latest.get('number')}**"
            )

        if successful:
            lines.append(
                f"Last successful: **#{successful.get('number')}**"
            )

        if failed:
            lines.append(
                f"Last failed: **#{failed.get('number')}**"
            )

        return "\n".join(lines)

    def build_latest_build_response(
        self,
        build
    ):

        if not build:
            return (
                "This Jenkins job doesn't have "
                "any builds yet."
            )

        number = build.get("number")
        result = build.get("result")
        building = build.get("building")

        status = (
            "RUNNING"
            if building
            else result
        )

        timestamp = build.get(
            "timestamp"
        )

        if timestamp:

            date = datetime.fromtimestamp(
                timestamp / 1000
            ).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        else:
            date = "Unknown"

        return (
            f"**Build #{number}**\n\n"
            f"Status: **{status}**\n"
            f"Started: **{date}**"
        )

    def build_logs_response(
        self,
        job_name,
        build_number,
        logs
    ):

        if not logs:

            return (
                f"No console logs were found "
                f"for {job_name} build "
                f"#{build_number}."
            )

        lines = logs.splitlines()

        # Keep chatbot response manageable
        max_lines = 40

        if len(lines) > max_lines:

            lines = lines[-max_lines:]

            heading = (
                f"**Last {max_lines} lines** "
                f"from {job_name} build "
                f"#{build_number}:"
            )

        else:

            heading = (
                f"**Console output** from "
                f"{job_name} build #{build_number}:"
            )

        return (
            heading
            + "\n\n"
            + "\n".join(lines)
        )

    def build_failure_response(
        self,
        job_name,
        build,
        logs
    ):

        if not build:

            return (
                f"I couldn't find a build "
                f"for {job_name}."
            )

        build_number = build.get(
            "number"
        )

        result = build.get(
            "result"
        )

        if result != "FAILURE":

            return (
                f"**{job_name} build "
                f"#{build_number}** is not "
                f"marked as FAILURE.\n\n"
                f"Current result: **{result}**"
            )

        errors = self._find_error_lines(
            logs
        )

        response = (
            f"**{job_name} build "
            f"#{build_number} failed.**"
        )

        if errors:

            response += (
                "\n\nPossible error details:"
            )

            for error in errors:

                response += (
                    f"\n• {error}"
                )

        else:

            response += (
                "\n\nI couldn't identify a "
                "specific error from the "
                "console output."
            )

        return response

    def build_history_response(
        self,
        builds
    ):

        if not builds:
            return (
                "No build history was found."
            )

        lines = [
            "**Recent builds:**",
            ""
        ]

        for build in builds:

            number = build.get(
                "number"
            )

            result = build.get(
                "result"
            ) or "RUNNING"

            timestamp = build.get(
                "timestamp"
            )

            if timestamp:

                date = datetime.fromtimestamp(
                    timestamp / 1000
                ).strftime(
                    "%Y-%m-%d %H:%M"
                )

            else:
                date = "Unknown"

            lines.append(
                f"• Build #{number} — "
                f"**{result}** — {date}"
            )

        return "\n".join(lines)

    def build_unknown_response(self):

        return (
            "I can help you with Jenkins jobs, "
            "builds, status and logs. 🤖\n\n"
            "**Try asking:**\n\n"
            "• Show all Jenkins jobs\n"
            "• What is the status of ChatOps-Test-Job?\n"
            "• What is the latest build of ChatOps-Test-Job?\n"
            "• Show logs for ChatOps-Test-Job\n"
            "• Why did ChatOps-Test-Job fail?\n"
            "• Show recent builds of ChatOps-Test-Job"
        )

    def _convert_color_to_status(
        self,
        color
    ):

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

            "grey_anime": "RUNNING"
        }

        return mapping.get(
            color.lower(),
            color.upper()
        )

    def _find_error_lines(
        self,
        logs
    ):

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

        errors = []

        for line in logs.splitlines():

            lower_line = line.lower()

            if any(
                keyword in lower_line
                for keyword in keywords
            ):

                cleaned = line.strip()

                if (
                    cleaned
                    and cleaned not in errors
                ):

                    errors.append(
                        cleaned
                    )

            if len(errors) >= 5:
                break

        return errors
