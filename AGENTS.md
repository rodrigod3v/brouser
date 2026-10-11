# AGENTS.md — Brouser

## O que e

Browser com agente de IA autonomo (clone do padrao browser-use) integrado ao opencode.
Foco atual: **funcionar**. Beleza depois.

## Regras duras

1. Arquitetura hexagonal: ver `docs/ARCHITECTURE.md`. Dependencia so aponta para dentro.
   `domain/` e `agent/` NUNCA importam playwright/openai/typesafe_sdk (teste `test_architecture.py` guarda isso).
2. Config nova so via `src/brouser/config.py` + linha documentada em `.env.example`.
3. Toda acao nova: literal em `ActionKind` + branch no `ActionExecutor` + teste unitario.
4. Sem segredos no repo. `.env` e gitignored.
5. Commits/PRs: conventional commits. CI roda ruff + mypy + pytest (matrix py3.11/3.12, ubuntu+windows).

## Comandos

```bash
pip install -e ".[dev]" && playwright install chromium
ruff check . && ruff format --check .
mypy
pytest -m "not integration"     # CI default
pytest -m integration           # smoke browser real (local)
brouser doctor
```

## Estilo

- Python 3.11+, mypy strict, ruff (E,F,I,UP,B,SIM,RUF), line 100.
- Async em adapters de IO. Domain puro e sincrono.
- Docstring curta em portugues; identificadores em ingles.

## Memoria

Sessoes do agente vao para o vault Obsidian configurado em `BROUSER_OBSIDIAN_VAULT`
(default: `C:\Users\777\Documents\Obsidian\Brain-Brouser`). Decisoes de arquitetura
registrar em `Brain-Brouser/decisions/`.
