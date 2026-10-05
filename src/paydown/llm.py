from dataclasses import dataclass

from openai import OpenAI

from paydown.config import get_env

TOKEN_FACTORY_BASE_URL = "https://api.tokenfactory.nebius.com/v1/"
DEFAULT_REASONING_MODEL = "nvidia/nemotron-3-super-120b-a12b"
CHEAP_MODEL = "nvidia/Nemotron-3_5-Lightning"

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=TOKEN_FACTORY_BASE_URL,
            api_key=get_env("NEBIUS_API_KEY"),
        )
    return _client


@dataclass
class ChatMessage:
    role: str
    content: str


def llm_complete(
    messages: list[ChatMessage],
    model: str = DEFAULT_REASONING_MODEL,
) -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": m.role, "content": m.content} for m in messages],
    )
    return response.choices[0].message.content


def llm_complete_cheap(messages: list[ChatMessage]) -> str:
    return llm_complete(messages, model=CHEAP_MODEL)