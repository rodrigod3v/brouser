# Arquitetura & Design Patterns — Brouser

## 1. Diagrama de camadas

```
+-----------------------------------------------------------+
|                        CLI (cli.py)                       |  <- entrada, so parse
+------------------------------+----------------------------+
                               |
+==============================v==============================+
|                        APPLICATION                        |
|  agent/loop.py (AgentLoop)   <- orquestra o ciclo ReAct   |
+===+===========+===========+============+===========+======+
    |           |           |            |           |
+===v===+   +===v====+  +===v===+   +====v====+  +===v======+
|browser|   |  llm/  |  | jev/  |   | memory/ |  | actions/ |
|adapter|   | adapter|  |adapter|   | obsidian|  | executor |
+===+===+   +===+====+  +===+===+   +====+====+  +===+======+
    |           |           |            |           |
+===v===========v===========v============v===========v======+
|                    DOMAIN (domain/)                       |
|  models: Action, Step, TaskResult, ElementNode (puros)    |
+===========================================================+
    |
+===v========================================================+
|              INFRASTRUCTURE (externo)                     |
|  Playwright | OpenAI-compatible API | TypeSafe Jev | FS   |
+-----------------------------------------------------------+
```

Regra de ouro: **dependencia so aponta para baixo**. Domain nao importa nada de
infra. Ports (protocolos) definidos em `ports.py`, implementados nos adapters.

## 2. Estrutura de pastas

```
BROUSER/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                 # lint + types + tests (matrix)
│   │   ├── semantic-pr.yml        # PR title conventional commits
│   │   └── codeql.yml             # security scan
│   ├── dependabot.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/
│   ├── PRD.md
│   └── ARCHITECTURE.md
├── src/brouser/
│   ├── __init__.py                # __version__
│   ├── config.py                  # Settings (pydantic-settings, .env)
│   ├── cli.py                     # argparse: run/doctor/version
│   ├── ports.py                   # Protocols: Browser, LLM, Judge, Memory
│   ├── domain/
│   │   ├── __init__.py
│   │   └── models.py              # Action, Step, ElementNode, TaskResult
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── loop.py                # AgentLoop (orquestrador)
│   │   └── prompts.py             # system prompt builder
│   ├── browser/
│   │   ├── __init__.py
│   │   ├── controller.py          # PlaywrightBrowser (port Browser)
│   │   └── dom.py                 # DOMExtractor -> ElementNode[]
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py              # OpenAICompatibleLLM (port LLM)
│   │   └── router.py              # ModelRouter (free/paid/auto)
│   ├── jev/
│   │   ├── __init__.py
│   │   └── judge.py               # JevJudge (port Judge) via typesafe-sdk
│   ├── memory/
│   │   ├── __init__.py
│   │   └── obsidian.py            # ObsidianMemory (port Memory)
│   └── actions/
│       ├── __init__.py
│       └── executor.py            # ActionExecutor: Action -> browser calls
├── tests/
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_action_parser.py
│   │   ├── test_router.py
│   │   └── test_obsidian_memory.py
│   └── integration/
│       └── test_smoke_browser.py  # marcado, fora do CI default
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
└── README.md
```

## 3. Design patterns aplicados

| Pattern | Onde | Por que |
|---------|------|---------|
| **Ports & Adapters (Hexagonal)** | `ports.py` + adapters | trocar Playwright/LLM/Obsidian sem tocar no loop |
| **Strategy** | `llm/router.py` | selecao free/paid/auto intercambiavel |
| **State Machine** | `agent/loop.py` | estados: OBSERVE -> DECIDE -> GATE -> ACT -> DONE/FAIL |
| **Command** | `domain/models.Action` + `actions/executor.py` | acao serializavel, logavel, rejeitavel |
| **Template Method** | `browser/dom.py` | pipeline extrair -> filtrar -> indexar |
| **Repository** | `memory/obsidian.py` | sessoes como recursos persistidos (markdown) |
| **Circuit Breaker (leve)** | `llm/client.py` retry com backoff | falha de provider nao trava agente |
| **DTO** | `domain/models.py` pydantic | fronteira tipada entre camadas |

## 4. Contratos (ports)

```python
class Browser(Protocol):
    async def goto(self, url: str) -> None: ...
    async def snapshot(self) -> Snapshot: ...  # url + ElementNode[]
    async def click(self, index: int) -> None: ...
    async def type_text(self, index: int, text: str) -> None: ...
    async def scroll(self, dy: int) -> None: ...
    async def back(self) -> None: ...
    async def page_text(self) -> str: ...


class LLM(Protocol):
    async def decide(self, task: str, history: list[Step], snap: Snapshot) -> Action: ...


class Judge(Protocol):  # Jev
    async def is_risky(self, action: Action, context: str) -> bool: ...
    async def is_task_done(self, task: str, page_text: str) -> bool: ...


class Memory(Protocol):
    async def save_session(self, result: TaskResult) -> Path: ...
```

## 5. Regras anti-regressao

1. Nenhum import de `playwright`/`openai` fora de `browser/` e `llm/` (enforced via teste de import).
2. `domain/` e `agent/` 100% cobertos por teste unitario puro (sem IO).
3. Toda acao nova = novo literal em `Action.kind` + handler no executor + teste.
4. Config nova so entra via `config.py` + linha documentada em `.env.example`.
5. CI verde obrigatorio; PR title conventional commit; squash merge.

## 6. Fluxo de decisao do loop

```
snapshot = browser.snapshot()
action   = llm.decide(task, history, snapshot)
if settings.jev_gate and jev.is_risky(action):  -> pede confirmacao usuario
browser executa action
history.append(step)
if action.kind == "done" or (jev_verify and jev.is_task_done(...)): finaliza
```
