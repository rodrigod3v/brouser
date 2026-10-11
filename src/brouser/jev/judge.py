"""JevJudge — adapter do port Judge usando TypeSafe Jev (System One).

Sem key configurada vira pass-through: nunca bloqueia, nunca confirma.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from brouser.domain.models import Action, ActionKind

if TYPE_CHECKING:
    from typesafe_sdk import AsyncTypeSafeClient

_RISKY_KINDS = {ActionKind.CLICK, ActionKind.TYPE, ActionKind.GOTO}


class JevJudge:
    def __init__(self, api_key: str, base_url: str = "", model: str = "jev-latest") -> None:
        self._api_key = api_key
        self._base_url = base_url or None
        self._model = model

    def _client(self) -> AsyncTypeSafeClient:
        """Client novo por chamada — `async with` fecha o client ao sair."""
        from typesafe_sdk import AsyncTypeSafeClient

        kwargs: dict[str, str] = {"api_key": self._api_key, "model": self._model}
        if self._base_url:
            kwargs["base_url"] = self._base_url
        return AsyncTypeSafeClient(**kwargs)  # type: ignore[arg-type]

    async def is_risky(self, action: Action, context: str) -> bool:
        """True = acao sensivel (pagamento, envio irreversivel, delete...)."""
        if not self._api_key or action.kind not in _RISKY_KINDS:
            return False
        from typesafe_sdk import Noul

        async with self._client() as client:
            resp = await client.system_one(
                state={
                    "page": context[:3000],
                    "action": action.model_dump_json(),
                },
                questions={
                    "risky": Noul(
                        instructions=(
                            "Esta acao de browser e irreversivel ou sensivel? "
                            "Ex.: finalizar compra, pagar, deletar, enviar mensagem publica, "
                            "submeter formulario com dados pessoais."
                        ),
                        criteria={
                            "true": "Pode causar efeito real irreversivel ou expor dados",
                            "false": "Navegacao/leitura/preenchimento inofensivo",
                        },
                    )
                },
            )
        return resp.nouls["risky"].noul >= 0.7

    async def is_task_done(self, task: str, answer: str, page_text: str) -> bool:
        """Segunda opiniao: a resposta realmente cumpre a tarefa?"""
        if not self._api_key:
            return False
        from typesafe_sdk import Noul

        async with self._client() as client:
            resp = await client.system_one(
                state={
                    "task": task,
                    "agent_answer": answer,
                    "page_excerpt": page_text[:3000],
                },
                questions={
                    "done": Noul(
                        instructions="A resposta do agente cumpre a tarefa pedida?",
                        criteria={
                            "true": "Resposta completa e apoiada pela pagina",
                            "false": "Incompleta, inventada ou sem relacao",
                        },
                    )
                },
            )
        return resp.nouls["done"].noul >= 0.7
