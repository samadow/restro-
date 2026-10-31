import json
import logging
import time
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class AIError(Exception):
    pass


def ask(system, user, history=None, temperature=0.4):
    """Send prompt to Groq and return answer as dict (model must answer in JSON)."""
    if not settings.GROQ_API_KEY:
        raise AIError("AI is not configured (GROQ_API_KEY is empty)")

    messages = [{"role": "system", "content": system}]
    messages += history or []
    messages.append({"role": "user", "content": user})

    body = json.dumps({
        "model": settings.GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }).encode("utf-8")

    request = urllib.request.Request(
        GROQ_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "restora/1.0",
        },
    )

    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.loads(response.read())
            break
        except urllib.error.HTTPError as e:
            error = e.read()[:500].decode("utf-8", "ignore")
            logger.error("Groq error %s: %s", e.code, error)

            # 429 - free tier limit per minute, 400 json_validate_failed - model wrote bad JSON
            if attempt == 0 and (e.code == 429 or "json_validate_failed" in error):
                time.sleep(retry_seconds(e) if e.code == 429 else 1)
                continue

            if e.code == 429:
                raise AIError("AI is busy now, try again in a minute")
            raise AIError(f"AI service error ({e.code})")
        except (urllib.error.URLError, TimeoutError) as e:
            logger.error("Groq is not available: %s", e)
            raise AIError("AI service is not available now")

    try:
        return json.loads(data["choices"][0]["message"]["content"])
    except (KeyError, IndexError, ValueError):
        raise AIError("AI returned wrong answer, try again")


def retry_seconds(error):
    try:
        return min(float(error.headers.get("retry-after", 5)), 10)
    except (TypeError, ValueError):
        return 5


def to_json(data):
    return json.dumps(data, ensure_ascii=False, default=str)
