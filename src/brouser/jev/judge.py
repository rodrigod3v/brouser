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
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client: AsyncTypeSafeClient | None = None

    async def _ensure(self) -> None:
        if self._client is None and self._api_key:
            from typesafe_sdk import AsyncTypeSafeClient

            self._client = AsyncTypeSafeClient(api_key=self._api_key)

    async def is_risky(self, action: Action, context: str) -> bool:
        """True = acao sensivel (pagamento, envio irreversivel, delete...)."""
        if not self._api_key or action.kind not in _RISKY_KINDS:
            return False
        await self._ensure()
        from typesafe_sdk import Noul

        assert self._client is not None
        async with self._client as client:
            resp = await client.system_one(
                model="jev-latest",
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
        await self._ensure()
        from typesafe_sdk import Noul

        assert self._client is not None
        async with self._client as client:
            resp = await client.system_one(
                model="jev-latest",
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
