"""Modelos de dominio puros — zero IO, zero imports de infra."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ActionKind(StrEnum):
    """Tipos de acao que o agente pode emitir."""

    GOTO = "goto"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    BACK = "back"
    WAIT = "wait"
    DONE = "done"
    FAIL = "fail"


class Action(BaseModel):
    """Comando serializavel emitido pelo LLM (pattern Command)."""

    kind: ActionKind
    index: int | None = None
    text: str | None = None
    url: str | None = None
    dy: int = 600
    answer: str | None = None
    reason: str = ""

    @classmethod
    def parse_loose(cls, raw: str) -> Action:
        """Parse tolerante: aceita JSON puro ou cercado por ``` fences.

        Levanta ValueError se nada parseavel for encontrado.
        """
        import json
        import re

        text = raw.strip()
        fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        candidate = fence.group(1) if fence else None
        if candidate is None:
            brace = re.search(r"\{.*\}", text, re.DOTALL)
            candidate = brace.group(0) if brace else None
        if candidate is None:
            msg = f"Nenhum JSON encontrado na resposta do LLM: {raw[:200]!r}"
            raise ValueError(msg)
        data: dict[str, Any] = json.loads(candidate)
        if "action" in data and "kind" not in data:
            data["kind"] = data.pop("action")
        return cls.model_validate(data)


class ElementNode(BaseModel):
    """Elemento interativo indexado da pagina."""

    index: int
    tag: str
    text: str = ""
    role: str = ""
    href: str = ""
    placeholder: str = ""

    def compact(self) -> str:
        parts = [f"[{self.index}] <{self.tag}>"]
        if self.text:
            parts.append(self.text[:80])
        if self.href:
            parts.append(f"href={self.href[:80]}")
        if self.placeholder:
            parts.append(f"ph={self.placeholder[:40]}")
        return " ".join(parts)


class Snapshot(BaseModel):
    """Estado observado da pagina em um step."""

    url: str
    title: str = ""
    elements: list[ElementNode] = Field(default_factory=list)

    def render(self, max_elements: int) -> str:
        lines = [f"URL: {self.url}", f"Title: {self.title}", "Elements:"]
        lines.extend(el.compact() for el in self.elements[:max_elements])
        return "\n".join(lines)


class Step(BaseModel):
    """Um ciclo observe->decide->act registrado."""

    n: int
    action: Action
    ok: bool = True
    error: str = ""
    ts: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def compact(self) -> str:
        status = "ok" if self.ok else f"ERRO: {self.error[:80]}"
        return f"step {self.n}: {self.action.kind} idx={self.action.index} -> {status}"


class TaskResult(BaseModel):
    """Resultado final de uma tarefa (persistido no Obsidian)."""

    task: str
    success: bool = False
    answer: str = ""
    steps: list[Step] = Field(default_factory=list)
    model: str = ""
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None

    def finish(self, success: bool, answer: str) -> None:
        self.success = success
        self.answer = answer
        self.finished_at = datetime.now(UTC)
