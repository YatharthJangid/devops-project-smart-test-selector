import json
import os
from urllib import error, request


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.4-mini")


class OpenAIAPIError(RuntimeError):
    pass


def generate_text(
    prompt,
    instructions=None,
    model=None,
    api_key=None,
    timeout=30,
):
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise OpenAIAPIError("OPENAI_API_KEY is required to call the AI API")

    payload = {
        "model": model or DEFAULT_MODEL,
        "input": prompt,
    }
    if instructions:
        payload["instructions"] = instructions

    api_request = request.Request(
        OPENAI_RESPONSES_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with request.urlopen(api_request, timeout=timeout) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise OpenAIAPIError(
            f"OpenAI API request failed with HTTP {exc.code}"
        ) from exc
    except error.URLError as exc:
        raise OpenAIAPIError(
            f"OpenAI API request failed: {exc.reason}"
        ) from exc

    output_text = _extract_output_text(response_data)
    if not output_text:
        raise OpenAIAPIError("OpenAI response did not include text output")

    return output_text


def _extract_output_text(response_data):
    if not isinstance(response_data, dict):
        return ""

    output_text = response_data.get("output_text")
    if isinstance(output_text, str):
        cleaned = output_text.strip()
        if cleaned:
            return cleaned

    return _find_text_item(response_data.get("output", []))


def _find_text_item(node):
    if isinstance(node, dict):
        if node.get("type") == "output_text":
            text = node.get("text", "")
            if isinstance(text, str):
                cleaned = text.strip()
                if cleaned:
                    return cleaned

        for value in node.values():
            found = _find_text_item(value)
            if found:
                return found
    elif isinstance(node, list):
        for item in node:
            found = _find_text_item(item)
            if found:
                return found

    return ""
