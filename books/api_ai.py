import json
import os
from functools import lru_cache

import requests
from dotenv import load_dotenv
from exceptions import APIKeyNotExists, ApiServiceError, UrlNotExists
from typesdef import api_key, url
from config import TIMEOUT

load_dotenv()


@lru_cache(maxsize=None)
def _check_url_exists() -> url:
    url = os.getenv("OPENROUTER_URL")
    if url is None:
        raise UrlNotExists
    return url


@lru_cache(maxsize=None)
def _check_api_key_exists() -> api_key:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key is None:
        raise APIKeyNotExists
    return api_key


system_promt_path = os.getenv("SYSTEM_PROMT")

if system_promt_path is None:
    raise ApiServiceError

with open(system_promt_path, "r", encoding="utf-8") as f:
    system_prompt = f.read()


def _get_googleapi_response(user_prompt: str) -> requests.Response:
    url = _check_url_exists()
    api_key = _check_api_key_exists()
    response = requests.post(
        url=url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                "model": "arcee-ai/trinity-mini:free",
                "messages": [
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": system_prompt,
                            },
                        ],
                    },
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": user_prompt}],
                    },
                ],
                "reasoning": {"enabled": True},
            }
        ),
        timeout=TIMEOUT
    )

    if response.status_code != requests.codes.ok:
        raise ApiServiceError
    return response


if __name__ == "__main__":
    response = _get_googleapi_response("Что-то китайское")
    print(response)
    response = response.json()
    response = response["choices"][0]["message"]
    print(response)
