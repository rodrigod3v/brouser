"""OpenAICompatibleLLM — adapter do port LLM com retry (circuit breaker leve)."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, cast

from brouser.agent.prompts import build_messages
from brouser.domain.models import Action, Snapshot, Step

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionMessageParam


class OpenAICompatibleLLM:
    """Funciona com qualquer endpoint OpenAI-compatible (ver .env.example)."""

    def __init__(self, base_url: str, api_key: str, model: str, max_elements: int = 80) -> None:
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key or "not-set")
        self._model = model
        self._max_elements = max_elements

    @property
    def model_name(self) -> str:
        return self._model

    async def decide(self, task: str, history: list[Step], snap: Snapshot) -> Action:
        messages: list[ChatCompletionMessageParam] = cast(
            "list[ChatCompletionMessageParam]",
            build_messages(task, history, snap, self._max_elements),
        )
        last_err: Exception | None = None
        for attempt in range(3):
            try:
                resp = await self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    temperature=0.1,
                )
                content = resp.choices[0].message.content or ""
                return Action.parse_loose(content)
            except ValueError as exc:
                # JSON invalido: devolve feedback ao modelo e tenta de novo
                messages = [
                    *messages,
                    cast("ChatCompletionMessageParam", {"role": "assistant", "content": content}),
                    cast(
                        "ChatCompletionMessageParam",
                        {
                            "role": "user",
                            "content": (
                                f"Resposta invalida ({exc}). Responda APENAS o JSON da acao."
                            ),
                        },
                    ),
                ]
                last_err = exc
            except Exception as exc:  # noqa: BLE001 - rede/provider: backoff e retenta
                last_err = exc
                await asyncio.sleep(2**attempt)
        msg = f"LLM falhou apos retries: {last_err}"
        raise RuntimeError(msg) from last_err
