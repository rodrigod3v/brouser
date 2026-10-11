"""ObsidianMemory — persiste sessoes como notas markdown no vault."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from brouser.domain.models import TaskResult


class ObsidianMemory:
    """Repository de sessoes: <vault>/sessions/YYYY-MM-DD/HHMMSS-slug.md"""

    def __init__(self, vault: Path) -> None:
        self._vault = vault

    @staticmethod
    def _slug(task: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", task.lower()).strip("-")
        return slug[:40] or "task"

    def _target(self, result: TaskResult) -> Path:
        day = result.started_at.strftime("%Y-%m-%d")
        stamp = result.started_at.strftime("%H%M%S")
        folder = self._vault / "sessions" / day
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{stamp}-{self._slug(result.task)}.md"

    def render_note(self, result: TaskResult) -> str:
        status = "success" if result.success else "fail"
        lines = [
            "---",
            f'task: "{result.task.replace(chr(34), chr(39))}"',
            f"status: {status}",
            f"model: {result.model}",
            f"date: {result.started_at.isoformat()}",
            f"steps: {len(result.steps)}",
            "tags: [brouser, session]",
            "---",
            "",
            f"# {result.task}",
            "",
            f"**Status:** {status} | **Modelo:** {result.model} | **Steps:** {len(result.steps)}",
            "",
            "## Resposta final",
            "",
            result.answer or "(sem resposta)",
            "",
            "## Steps",
            "",
            "| # | Acao | Detalhe | Status |",
            "|---|------|---------|--------|",
        ]
        for s in result.steps:
            detail = s.action.text or s.action.url or s.action.answer or ""
            detail = detail.replace("|", "\\|")[:60]
            lines.append(f"| {s.n} | {s.action.kind} | {detail} | {'ok' if s.ok else 'ERRO'} |")
        lines += ["", "Links: [[index]]"]
        return "\n".join(lines)

    async def save_session(self, result: TaskResult) -> Path:
        path = self._target(result)
        path.write_text(self.render_note(result), encoding="utf-8")
        return path
