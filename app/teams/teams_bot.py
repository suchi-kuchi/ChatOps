
import asyncio
import json
import os
import re

from microsoft_teams.apps import App, FastAPIAdapter

# Optional: local Teams-like test page (no tenant needed). Set ENABLE_DEVTOOLS=true.
# Package: pip install microsoft-teams-devtools   (verify name in the Teams SDK docs)
try:
    from microsoft_teams.devtools import DevToolsPlugin
except ImportError:  # devtools not installed
    DevToolsPlugin = None

# Optional "typing..." indicator. Falls back to a text message if unavailable.
try:
    from microsoft_teams.api import TypingActivityInput
except ImportError:
    TypingActivityInput = None


# keep Teams messages readable (hard limit is ~28 KB)
MAX_REPLY_CHARS = 3500
MENTION_RE = re.compile(r"<at>.*?</at>", re.IGNORECASE)


def clean_text(raw: str) -> str:
    """Remove '<at>BotName</at>' (added when the bot is @mentioned in a channel)."""
    text = MENTION_RE.sub("", raw or "")
    return re.sub(r"\s+", " ", text).strip()


def format_reply(result) -> str:
    """Turn whatever chat_service.answer() returns into a Teams-friendly string."""
    if isinstance(result, dict):
        for key in ("answer", "response", "message", "text"):
            if isinstance(result.get(key), str):
                result = result[key]
                break
        else:
            result = json.dumps(result, indent=2, default=str)
    elif not isinstance(result, str):
        result = str(result)

    # Long output (e.g. build logs): show the TAIL, which is usually where errors are.
    if len(result) > MAX_REPLY_CHARS:
        result = "...(truncated, showing last part)...\n" + \
            result[-MAX_REPLY_CHARS:]

    # Multi-line output looks best in a code block.
    if "\n" in result and not result.startswith("```"):
        result = f"```\n{result}\n```"
    return result


def create_teams_app(fastapi_app, chat_service) -> App:
    adapter = FastAPIAdapter(app=fastapi_app)

    plugins = []
    if DevToolsPlugin and os.getenv("ENABLE_DEVTOOLS", "true").lower() == "true":
        plugins.append(DevToolsPlugin())

    # Credentials (CLIENT_ID, CLIENT_SECRET, TENANT_ID) are read from env vars.
    # They are NOT needed for DevTools-only local testing.
    teams_app = App(http_server_adapter=adapter, plugins=plugins)

    @teams_app.on_message
    async def handle_teams_message(ctx):
        question = clean_text(ctx.activity.text)

        if not question:
            await ctx.send("Please enter a Jenkins question, e.g. `show logs for build 25`.")
            return

        # Tell the user we're working (Jenkins calls can be slow).
        if TypingActivityInput:
            await ctx.send(TypingActivityInput())
        else:
            await ctx.send("Fetching from Jenkins...")

        try:
            result = await asyncio.to_thread(chat_service.answer, question)
            await ctx.send(format_reply(result))
        except Exception as exc:  # never let the bot go silent
            await ctx.send(f"Sorry, something went wrong: {exc}")

    return teams_app
