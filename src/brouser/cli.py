"""CLI brouser: run / doctor / version."""

from __future__ import annotations

import argparse
import asyncio
import shutil
import sys

from brouser import __version__
from brouser.config import ModelRouting, get_settings
from brouser.domain.models import Action


def _confirm_cli(action: Action) -> bool:
    resp = input(f"  Confirmar acao sensivel {action.kind} idx={action.index}? [s/N] ")
    return resp.strip().lower() in {"s", "sim", "y", "yes"}


async def _run(task: str, routing_override: str | None) -> int:
    from brouser.agent.loop import AgentLoop
    from brouser.browser.controller import PlaywrightBrowser
    from brouser.jev.judge import JevJudge
    from brouser.llm.router import ModelRouter
    from brouser.memory.obsidian import ObsidianMemory

    settings = get_settings()
    if routing_override:
        settings.model_routing = ModelRouting(routing_override)
    if not settings.llm_api_key:
        print("ERRO: LLM_API_KEY vazio. Copie .env.example -> .env e preencha.")
        return 2

    llm = ModelRouter(settings).current()
    judge = JevJudge(settings.typesafe_api_key) if settings.typesafe_api_key else None
    memory = ObsidianMemory(settings.vault_path) if settings.vault_path else None

    print(f"brouser v{__version__} | modelo: {llm.model_name} | task: {task}")
    async with PlaywrightBrowser(settings) as browser:
        loop = AgentLoop(
            settings,
            browser,
            llm,
            judge=judge,
            memory=memory,
            confirm=_confirm_cli,
        )
        result = await loop.run(task)

    print()
    print("=" * 60)
    print("SUCESSO" if result.success else "FALHOU", f"em {len(result.steps)} steps")
    print(result.answer)
    return 0 if result.success else 1


def _doctor() -> int:
    settings = get_settings()
    ok = True

    def check(label: str, good: bool, hint: str = "") -> None:
        nonlocal ok
        print(f"  [{'ok' if good else 'X'}] {label}" + (f" — {hint}" if hint and not good else ""))
        ok = ok and good

    print("brouser doctor:")
    check("LLM_API_KEY", bool(settings.llm_api_key), "preencha no .env")
    check("tier free (opcional)", settings.free_tier_configured, "LLM_FREE_* no .env")
    check("TYPESAFE_API_KEY (opcional)", bool(settings.typesafe_api_key), "gate Jev desligado")
    check("vault Obsidian", settings.vault_path is not None, "BROUSER_OBSIDIAN_VAULT no .env")
    if settings.vault_path:
        check("vault existe", settings.vault_path.exists(), "crie a pasta do vault")
    check("npx (skills)", shutil.which("npx") is not None, "instale Node.js")
    print("playwright: rode 'playwright install chromium' uma vez")
    return 0 if ok else 1


def main() -> None:
    parser = argparse.ArgumentParser(prog="brouser", description="Browser com agente IA autonomo")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="executa uma tarefa no browser")
    p_run.add_argument("task", help="ordem em linguagem natural")
    p_run.add_argument("--model", choices=["auto", "free", "paid"], default=None)

    sub.add_parser("doctor", help="verifica ambiente/config")
    sub.add_parser("version", help="mostra versao")

    args = parser.parse_args()
    if args.cmd == "run":
        sys.exit(asyncio.run(_run(args.task, args.model)))
    if args.cmd == "doctor":
        sys.exit(_doctor())
    if args.cmd == "version":
        print(__version__)
        sys.exit(0)


if __name__ == "__main__":
    main()
