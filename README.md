# Brouser

**Browser proprio com agente de IA autonomo** — estilo [browser-use](https://github.com/browser-use/browser-use),
integrado ao ecossistema opencode.

Voce da a ordem em linguagem natural. O agente abre o browser, navega, pesquisa,
clica, digita, preenche formularios, extrai dados e devolve a resposta. Sozinho.

```
$ brouser run "pesquise o preco da RTX 5090 no google e me de o top 3"

brouser v0.1.0 | modelo: gpt-4o-mini | task: pesquise o preco da RTX 5090...
  [step 1: goto idx=None -> ok]
  [step 2: type idx=4 -> ok]
  [step 3: click idx=7 -> ok]
  [step 4: scroll -> ok]
  [step 5: done idx=None -> ok]
  sessao salva: C:\...\Brain-Brouser\sessions\2026-10-11\213045-pesquise-o-preco.md

============================================================
SUCESSO em 5 steps
Top 3 precos RTX 5090: 1) ...
```

---

## Por que existe

| Alternativa | Problema | Brouser |
|-------------|----------|---------|
| Script Selenium/Playwright | fragil, quebra com qualquer mudanca de layout | LLM decide a acao olhando o DOM real a cada step |
| Servicos fechados de automacao | caros, seus dados saem da sua maquina | roda local, suas keys, seus modelos |
| browser-use original | ecossistema/config proprios | integrado ao opencode: mesmas keys, modelos free e pagos, julgamentos Jev, memoria no Obsidian |

## Features

- **Loop agente autonomo**: observa pagina → decide acao (JSON) → executa → repete ate concluir
- **DOM indexado**: cada elemento interativo vira `[N]`; o LLM clica/digita por indice
- **Multi-provider**: qualquer API OpenAI-compatible (OpenAI, OpenRouter, opencode zen, Groq, Ollama local)
- **Router de modelos**: tier `free` / `paid` / `auto` (comeca gratis, escala se precisar)
- **Jev (TypeSafe)**: julgamentos deterministicos baratos —
  gate de acoes sensiveis (compra, delete, submit pedem sua confirmacao) e
  segunda opiniao de "tarefa concluida"
- **Memoria Obsidian**: cada sessao vira nota markdown no vault `Brain-Brouser`
- **Browser persistente**: cookies/login sobrevivem entre sessoes (perfil local)
- **Skills**: descoberta de capacidades via [find-skills](https://agenticskills.io/skills/find-skills)

## Arquitetura (resumo)

Hexagonal — dependencia so aponta para dentro. Detalhes em [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

```
CLI ──> AgentLoop ──┬──> Browser (Playwright)   controle real do Chromium
                    ├──> LLM (OpenAI-compat)    decide proxima acao
                    ├──> Judge (Jev/TypeSafe)   gate de risco + verificacao
                    └──> Memory (Obsidian)      sessoes em markdown
```

Patterns: Ports & Adapters, Strategy (router), State Machine (loop), Command (acoes), Repository (memoria).

## Setup

Pre-requisitos: Python 3.11+, Node 20+ (opcional, pra skills).

```bash
git clone https://github.com/rodrigod3v/brouser.git
cd brouser

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

pip install -e ".[dev]"
playwright install chromium

cp .env.example .env            # preencha as keys — guia: docs/KEYS.md
```

Validar instalacao:

```bash
brouser doctor
```

Saida esperada: tudo `[ok]`. Se algo falhar, o doctor diz o que falta.

## Uso

```bash
# tarefa livre
brouser run "abra o github, pesquise browser-use e me diga quantas stars tem"

# forcar tier de modelo
brouser run "..." --model free     # so modelo gratuito
brouser run "..." --model paid     # so modelo pago
brouser run "..." --model auto     # default: free primeiro, escala se estagnar

# utilitarios
brouser doctor      # verifica keys, vault, node, playwright
brouser version
```

Acoes sensiveis (finalizar compra, deletar, submeter dados) pausam o agente e
pedem sua confirmacao no terminal — desde que `TYPESAFE_API_KEY` esteja no `.env`.

## Configuracao

Tudo via `.env` (copiado do `.env.example`). Variaveis principais:

| Variavel | Default | O que faz |
|----------|---------|-----------|
| `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` | — | provider principal (obrigatorio) |
| `LLM_FREE_*` | vazio | tier gratuito (opcional) |
| `MODEL_ROUTING` | `auto` | `auto` / `free` / `paid` |
| `TYPESAFE_API_KEY` | vazio | liga gates Jev |
| `JEV_GATE_ENABLED` | `true` | confirma acoes sensiveis |
| `JEV_VERIFY_DONE` | `false` | Jev valida resposta final |
| `BROUSER_HEADLESS` | `false` | `true` = sem janela |
| `BROUSER_MAX_STEPS` | `25` | limite de acoes por tarefa |
| `BROUSER_OBSIDIAN_VAULT` | — | pasta do vault de memoria |

Lista completa e comentada: [.env.example](.env.example).
**Onde conseguir cada key:** [docs/KEYS.md](docs/KEYS.md).

## Desenvolvimento

```bash
# qualidade — o CI bloqueia merge sem tudo verde
ruff check . && ruff format --check .
mypy
pytest -m "not integration"     # unitarios (default CI)
pytest -m integration           # smoke com browser real

pre-commit install              # hooks locais
```

Regras duras em [AGENTS.md](AGENTS.md). Convencional commits obrigatorio
(titulo do PR validado no CI): `feat:`, `fix:`, `docs:`, `refactor:`, ...

### Estrutura

```
src/brouser/
├── cli.py           # entrada: run/doctor/version
├── config.py        # Settings (.env) — unica porta de config
├── ports.py         # contratos (Browser, LLM, Judge, Memory)
├── domain/          # modelos puros, zero IO
├── agent/           # loop ReAct + prompts
├── browser/         # Playwright + extracao de DOM
├── llm/             # cliente OpenAI-compat + router free/paid
├── jev/             # judge TypeSafe
├── memory/          # Obsidian
└── actions/         # executor de acoes
```

## Roadmap

- [x] **M1** scaffold, loop funcional, CI, Jev, Obsidian, find-skills
- [ ] **M2** gate Jev completo, escalacao auto free→paid, benchmark de tarefas
- [ ] **M3** UI web local, multi-tab, stealth anti-bot
- [ ] **M4** marketplace de skills proprio, replay de sessoes

## Troubleshooting

| Sintoma | Causa provavel | Fix |
|---------|----------------|-----|
| `LLM_API_KEY vazio` | `.env` ausente | `cp .env.example .env` e preencher |
| Playwright nao abre | browser nao instalado | `playwright install chromium` |
| Gate Jev nunca ativa | sem `TYPESAFE_API_KEY` | console.typesafe.ai (opcional) |
| Sessao nao salva | `BROUSER_OBSIDIAN_VAULT` errado | `brouser doctor` valida caminho |
| `npx skills` falha | Node < 22 | upgrade Node ou skill ja instalada em `~/.claude/skills` |

Mais: [Brain-Brouser/runbooks](https://github.com/rodrigod3v/brouser) (vault local).

## Docs

- [PRD](docs/PRD.md) — produto, requisitos, metricas
- [Arquitetura & design patterns](docs/ARCHITECTURE.md)
- [Onde pegar as keys](docs/KEYS.md)
- [AGENTS.md](AGENTS.md) — regras para agentes/contribuidores

## Licenca

MIT
