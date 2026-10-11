# KEYS — onde pegar cada chave do `.env`

> Guia definitivo de credenciais do Brouser.
> Regra: chave real so no `.env` (gitignored). NUNCA commitar.

## Mapa rapido

| Variavel | Obrigatoria? | Onde pegar | Custo |
|----------|--------------|-----------|-------|
| `LLM_API_KEY` | SIM | provider a escolha (secao 1) | varia |
| `LLM_BASE_URL` | SIM | vem do provider (secao 1) | — |
| `LLM_MODEL` | SIM | nome do modelo no provider | — |
| `LLM_FREE_*` | opcional | provider com tier free (secao 2) | gratis |
| `TYPESAFE_API_KEY` | recomendado | console.typesafe.ai (secao 3) | free tier |
| `BROUSER_OBSIDIAN_VAULT` | recomendado | caminho local, sem key (secao 4) | gratis |

---

## 1. LLM principal (`LLM_BASE_URL` + `LLM_API_KEY` + `LLM_MODEL`)

Qualquer provider **OpenAI-compatible** serve. Pegue UM:

### 1a. OpenCode Zen (recomendado — mesmas keys do nosso opencode)
- O que e: proxy de modelos do opencode; usa a conta/key que ja temos aqui.
- Onde: https://opencode.ai → dashboard → API key. Endpoint Zen documentado em https://opencode.ai/docs/zen/
- Preencher:
  ```
  LLM_BASE_URL=<endpoint zen do docs, formato .../v1>
  LLM_API_KEY=<sua key opencode>
  LLM_MODEL=<modelo disponivel no zen, ex.: qwen3-coder, gpt-5-mini>
  ```
- Vantagem: zero conta nova, mesma billing do opencode, tem modelos free e pagos.

### 1b. OpenRouter
- Onde: https://openrouter.ai/keys → "Create Key"
- Preencher:
  ```
  LLM_BASE_URL=https://openrouter.ai/api/v1
  LLM_API_KEY=sk-or-...
  LLM_MODEL=openai/gpt-4o-mini        # ou qualquer modelo do catalogo
  ```
- Vantagem: um so endpoint pra centenas de modelos; varios free (secao 2).

### 1c. OpenAI direto
- Onde: https://platform.openai.com/api-keys → "Create new secret key"
- Preencher:
  ```
  LLM_BASE_URL=https://api.openai.com/v1
  LLM_API_KEY=sk-...
  LLM_MODEL=gpt-4o-mini
  ```

### 1d. Groq (rapido, tem free)
- Onde: https://console.groq.com/keys
- Preencher:
  ```
  LLM_BASE_URL=https://api.groq.com/openai/v1
  LLM_API_KEY=gsk_...
  LLM_MODEL=llama-3.3-70b-versatile
  ```

### 1e. Local (Ollama, sem key real)
- Onde: https://ollama.com → `ollama pull qwen3` → roda em localhost
- Preencher:
  ```
  LLM_BASE_URL=http://localhost:11434/v1
  LLM_API_KEY=ollama            # qualquer string nao-vazia
  LLM_MODEL=qwen3
  ```

---

## 2. Tier gratuito (`LLM_FREE_*`)

Router `MODEL_ROUTING=auto` comeca no free e escala pro pago se estagnar.
Opcoes de modelos free:

| Provider | Modelo free | Onde |
|----------|------------|------|
| OpenRouter | modelos com sufixo `:free` (lista: https://openrouter.ai/models?q=free) | mesma key da secao 1b |
| OpenCode Zen | modelos marcados free no catalogo | mesma key da secao 1a |
| Groq | rate limit free generoso | mesma key da secao 1d |
| Ollama | tudo free (local, usa sua GPU/CPU) | secao 1e |

Exemplo (OpenRouter free):
```
LLM_FREE_BASE_URL=https://openrouter.ai/api/v1
LLM_FREE_API_KEY=sk-or-...              # mesma key do pago
LLM_FREE_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

Sem `LLM_FREE_*` preenchido: `auto` cai direto no pago. Sem erro.

---

## 3. Jev / TypeSafe (`TYPESAFE_API_KEY`)

Pra que serve: julgamentos deterministicos baratos —
gate de acoes sensiveis (compra/delete/submit pedem confirmacao) e
verificacao de "tarefa concluida" (`JEV_VERIFY_DONE=true`).

1. Criar conta: https://console.typesafe.ai/
2. Gerar API key no dashboard
3. Preencher:
   ```
   TYPESAFE_API_KEY=tsk-...
   ```

Sem key: agente funciona normal, so sem os gates (fail-open, nao trava).
Docs: https://docs.typesafe.ai/

---

## 4. Obsidian (`BROUSER_OBSIDIAN_VAULT`)

Sem key — so caminho local. Default ja criado:
```
BROUSER_OBSIDIAN_VAULT=C:\Users\777\Documents\Obsidian\Brain-Brouser
```
Cada sessao do agente vira nota em `Brain-Brouser/sessions/<data>/`.

---

## 5. Checklist final

```bash
cp .env.example .env     # 1. copiar
# 2. preencher LLM_* (secao 1) — minimo obrigatorio
# 3. opcional: LLM_FREE_* (secao 2), TYPESAFE_API_KEY (secao 3)
brouser doctor           # 4. validar — tudo [ok]
brouser run "abre google.com e pesquisa opencode ai"   # 5. primeiro run
```

## 6. Seguranca

- `.env` esta no `.gitignore` — confirme com `git check-ignore .env`
- CI nao le `.env`; segredos de CI vao em GitHub Secrets se necessario
- Key vazou? Revogue no console do provider e gere outra
