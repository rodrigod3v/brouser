"""AgentLoop — maquina de estados OBSERVE -> DECIDE -> GATE -> ACT -> DONE/FAIL."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

from brouser.actions.executor import ActionExecutor
from brouser.config import Settings
from brouser.domain.models import Action, ActionKind, Snapshot, Step, TaskResult
from brouser.ports import LLM, Browser, Judge, Memory


class AgentLoop:
    def __init__(
        self,
        settings: Settings,
        browser: Browser,
        llm: LLM,
        judge: Judge | None = None,
        memory: Memory | None = None,
        confirm: Callable[[Action], bool] | None = None,
    ) -> None:
        self._s = settings
        self._browser = browser
        self._llm = llm
        self._judge = judge
        self._memory = memory
        self._confirm: Callable[[Action], bool] = confirm or (lambda action: True)

    async def run(self, task: str) -> TaskResult:
        result = TaskResult(task=task, model=getattr(self._llm, "model_name", "?"))
        executor = ActionExecutor(self._browser)
        try:
            for n in range(1, self._s.brouser_max_steps + 1):
                snap = await self._browser.snapshot()
                step = await self._step(n, task, result.steps, snap, executor)
                result.steps.append(step)
                print(f"  [{step.compact()}]")
                if not step.ok:
                    continue
                if step.action.kind in (ActionKind.DONE, ActionKind.FAIL):
                    ok = step.action.kind == ActionKind.DONE
                    answer = step.action.answer or ""
                    if ok and self._s.jev_verify_done and self._judge:
                        page = await self._browser.page_text()
                        if not await self._judge.is_task_done(task, answer, page):
                            result.steps.append(
                                Step(
                                    n=n,
                                    action=step.action,
                                    ok=False,
                                    error="Jev rejeitou conclusao; continuando",
                                )
                            )
                            continue
                    result.finish(ok, answer)
                    break
            else:
                result.finish(False, f"Limite de {self._s.brouser_max_steps} steps atingido")
        finally:
            if self._memory and not self._s.brouser_memory_disabled:
                try:
                    path = await self._memory.save_session(result)
                    print(f"  sessao salva: {path}")
                except Exception as exc:  # noqa: BLE001 - memoria nao derruba run
                    print(f"  aviso: falha ao salvar sessao: {exc}")
        return result

    async def _step(
        self, n: int, task: str, history: list[Step], snap: Snapshot, executor: ActionExecutor
    ) -> Step:
        try:
            action = await self._llm.decide(task, history, snap)
        except Exception as exc:  # noqa: BLE001
            return Step(n=n, action=self._fail_action(), ok=False, error=str(exc))

        if (
            self._s.jev_gate_enabled
            and self._judge
            and action.kind not in (ActionKind.DONE, ActionKind.FAIL)
        ):
            try:
                if await self._judge.is_risky(action, snap.url):
                    print(f"  !! acao sensivel (Jev): {action.kind} idx={action.index}")
                    if not await asyncio.to_thread(self._confirm, action):
                        return Step(n=n, action=action, ok=False, error="rejeitada pelo usuario")
            except Exception as exc:  # noqa: BLE001 - gate falhou aberto, nao trava
                print(f"  aviso: gate Jev falhou ({exc}); seguindo")

        try:
            await executor.execute(action)
        except Exception as exc:  # noqa: BLE001
            return Step(n=n, action=action, ok=False, error=str(exc))
        return Step(n=n, action=action)

    @staticmethod
    def _fail_action() -> Action:
        return Action(kind=ActionKind.FAIL, answer="llm indisponivel")
