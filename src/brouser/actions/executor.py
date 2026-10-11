"""ActionExecutor — traduz Action (Command) em chamadas no port Browser."""

from __future__ import annotations

from brouser.domain.models import Action, ActionKind
from brouser.ports import Browser


class ActionExecutor:
    def __init__(self, browser: Browser) -> None:
        self._b = browser

    async def execute(self, action: Action) -> None:
        """Levanta ValueError em acao malformada; erro de browser propaga."""
        match action.kind:
            case ActionKind.GOTO:
                if not action.url:
                    raise ValueError("goto exige url")
                await self._b.goto(action.url)
            case ActionKind.CLICK:
                self._require_index(action)
                await self._b.click(action.index or 0)
            case ActionKind.TYPE:
                self._require_index(action)
                if action.text is None:
                    raise ValueError("type exige text")
                await self._b.type_text(action.index or 0, action.text)
            case ActionKind.SCROLL:
                await self._b.scroll(action.dy)
            case ActionKind.BACK:
                await self._b.back()
            case ActionKind.WAIT:
                await self._b.wait(1500)
            case ActionKind.DONE | ActionKind.FAIL:
                pass  # loop trata
            case _:
                raise ValueError(f"acao desconhecida: {action.kind}")

    @staticmethod
    def _require_index(action: Action) -> None:
        if action.index is None:
            raise ValueError(f"{action.kind} exige index")
