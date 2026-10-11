# PRD — Brouser

> Browser proprio com agente de IA autonomo (estilo browser-use) integrado ao opencode.
> Versao: 0.1.0 | Status: Draft | Dono: rodrigod3v

## 1. Visao

Browser controlado por agente de IA autonomo. Usuario da ordem em linguagem natural
("pesquisa X", "preenche formulario Y", "clica em Z") e o agente navega, clica,
digita, extrai e responde — usando os modelos e API keys ja configurados no
ambiente opencode do usuario (gratuitos e pagos).

Foco desta fase: **funcionar**. Beleza depois.

## 2. Problema

Automacao de browser hoje exige ou script fragil (Selenium/Playwright puro) ou
servico fechado caro. browser-use provou o padrao "LLM + DOM indexado + loop de
acoes". Queremos isso sob nosso controle: nosso repo, nossas keys, nossos modelos,
nossos dados (Obsidian), julgamentos deterministicos baratos (Jev) onde LLM grande
e desperdicio.

## 3. Objetivos

| ID | Objetivo | Metrica |
|----|----------|---------|
| O1 | Agente completa tarefa web simples fim-a-fim | Task success rate em benchmark interno |
| O2 | Rodar com qualquer provider OpenAI-compatible | 1 .env, zero mudanca de codigo |
| O3 | Custo minimo por tarefa | Jev filtra decisoes triviais; modelo pago so quando preciso |
| O4 | Zero regressao por mudanca de arquitetura | CI verde obrigatorio, cobertura em modulos core |
| O5 | Memoria persistente das sessoes | Todo run gera nota no Obsidian Brain-Brouser |

## 4. Nao-objetivos (fase 1)

- UI grafica bonita / extensao de browser
- Multi-agente / paralelismo de sessoes
- Mobile
- Cloud/hosted

## 5. Usuarios e casos de uso

**Usuario:** desenvolvedor (nos) rodando CLI.

Casos:
1. `brouser run "pesquise o preco do RTX 5090 no google e me de top 3"` — agente navega, extrai, responde.
2. `brouser run "abra site X e preencha formulario com dados Y"` — agente clica/digita.
3. `brouser run "..." --model free` — rota para modelo gratuito.
4. Sessao inteira logada no Obsidian para revisao.

## 6. Requisitos funcionais

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| F1 | Controlar Chromium via Playwright (launch, goto, click, type, scroll, back) | P0 |
| F2 | Extrair DOM interativo com indices estaveis (elemento [12] = botao X) | P0 |
| F3 | Loop agente: snapshot -> LLM decide acao (JSON) -> executa -> repete ate `done` | P0 |
| F4 | Router de modelos: tier `free` / `paid` / `auto` via .env | P0 |
| F5 | Gate de seguranca via Jev: acoes sensiveis (submit, compra, delete) exigem confirmacao | P1 |
| F6 | Verificacao de conclusao via Jev (Noul: "tarefa concluida?") como segunda opiniao | P1 |
| F7 | Persistir cada sessao em markdown no Obsidian vault configuravel | P1 |
| F8 | CLI: `run`, `doctor`, `version` | P0 |
| F9 | Skill discovery: agente pode invocar `npx skills find/add` quando falta capacidade | P2 |

## 7. Requisitos nao-funcionais

- Python 3.11+, codigo tipado (mypy strict em modulos core)
- Lint: ruff; formatacao: ruff format
- CI bloqueia merge sem: lint ok, types ok, testes ok, titulo PR conventional commits
- Segredos so em `.env` (gitignored); `.env.example` documenta tudo
- Arquitetura em camadas; dependencia aponta para dentro (ver ARCHITECTURE.md)

## 8. Fluxo principal (happy path)

```
usuario -> CLI -> AgentLoop
  1. BrowserController abre pagina
  2. DOMExtractor gera lista indexada de elementos
  3. LLMClient envia [task + historico + elementos] -> recebe acao JSON
  4. (opcional) JevGate avalia risco da acao
  5. ActionExecutor executa no browser
  6. Repete 2-5 ate action=done ou max_steps
  7. ObsidianMemory grava nota da sessao
  8. CLI imprime resposta final
```

## 9. Riscos

| Risco | Mitigacao |
|-------|-----------|
| LLM retorna JSON invalido | Parser tolerante + retry com feedback |
| Sites com anti-bot | headless=False default, user-agent real, stealth futuro |
| Custo de tokens com DOM grande | Truncar/compactar DOM, Jev pra decisoes baratas |
| Indice de elemento muda apos navegacao | Re-extrair DOM a cada step; invalidar indices |

## 10. Roadmap

- **M1 (agora):** scaffold, loop basico funcional, CI, .env, Obsidian, Jev instalado
- **M2:** gate Jev completo, router auto free/paid, benchmark de tarefas
- **M3:** UI minima (web local), multi-tab, stealth
- **M4:** marketplace de skills do proprio brouser, replay de sessoes
