"""Extracao de DOM interativo — pipeline: extrair -> filtrar -> indexar."""

from __future__ import annotations

from typing import Any

from brouser.domain.models import ElementNode

JS_EXTRACT = """
() => {
  const ATTR = 'data-brouser-idx';
  document.querySelectorAll(`[${ATTR}]`).forEach(el => el.removeAttribute(ATTR));
  const sel = 'a, button, input, textarea, select, [role="button"], [role="link"], '
    + '[onclick], [tabindex]:not([tabindex="-1"]), summary';
  const out = [];
  let idx = 0;
  for (const el of document.querySelectorAll(sel)) {
    const r = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    if (r.width < 2 || r.height < 2) continue;
    if (style.visibility === 'hidden' || style.display === 'none') continue;
    el.setAttribute(ATTR, String(idx));
    out.push({
      index: idx,
      tag: el.tagName.toLowerCase(),
      text: (el.innerText || el.value || '').trim().slice(0, 200),
      role: el.getAttribute('role') || '',
      href: el.getAttribute('href') || '',
      placeholder: el.getAttribute('placeholder') || ''
    });
    idx++;
    if (idx >= 300) break;
  }
  return out;
}
"""


def parse_elements(raw: list[dict[str, Any]]) -> list[ElementNode]:
    """Filtra/converte payload JS bruto em ElementNode validados."""
    nodes: list[ElementNode] = []
    for item in raw:
        try:
            nodes.append(ElementNode.model_validate(item))
        except Exception:  # noqa: BLE001 - payload JS hostil nao pode derrubar o step
            continue
    return nodes
