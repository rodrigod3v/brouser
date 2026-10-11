"""Construcao de prompts do loop (puro, testavel)."""

from __future__ import annotations

from brouser.domain.models import Snapshot, Step

SYSTEM_PROMPT = """Voce e um agente que controla um browser. A cada passo voce recebe:
- a TAREFA do usuario
- o HISTORICO de acoes
- a lista de ELEMENTOS interativos da pagina, numerados como [N]

Responda APENAS com um JSON de UMA acao:
{"kind": "goto",   "url": "https://...", "reason": "..."}
{"kind": "click",  "index": N, "reason": "..."}
{"kind": "type",   "index": N, "text": "texto a digitar", "reason": "..."}
{"kind": "scroll", "dy": 600, "reason": "..."}         # dy negativo sobe
{"kind": "back",   "reason": "..."}
{"kind": "wait",   "reason": "..."}
{"kind": "done",   "answer": "resposta final ao usuario", "reason": "..."}
{"kind": "fail",   "answer": "por que nao deu", "reason": "..."}

Regras:
- UMA acao por resposta. Nada de texto fora do JSON.
- Use so indices presentes na lista de ELEMENTOS.
- Prefira elementos visiveis no topo; use scroll se o alvo nao aparecer.
- Quando tiver a resposta final, emita done com answer completo.
- Nunca invente URL; se nao souber, use um buscador.
"""


def build_messages(
    task: str, history: list[Step], snap: Snapshot, max_elements: int
) -> list[dict[str, str]]:
    hist = "\n".join(s.compact() for s in history[-10:]) or "(vazio)"
    user = (
        f"TAREFA: {task}\n\n"
        f"HISTORICO (ultimos 10):\n{hist}\n\n"
        f"PAGINA ATUAL:\n{snap.render(max_elements)}\n\n"
        "Qual a proxima acao? Responda APENAS o JSON."
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]
