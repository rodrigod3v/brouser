"""Guarda anti-regressao: camadas internas nao podem importar infra."""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "brouser"

FORBIDDEN = {
    "domain": {"playwright", "openai", "typesafe_sdk"},
    "agent": {"playwright", "openai", "typesafe_sdk"},
}


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module.split(".")[0])
    return mods


def test_camadas_puras_nao_importam_infra():
    violations = []
    for layer, banned in FORBIDDEN.items():
        for py in (SRC / layer).rglob("*.py"):
            bad = _imports(py) & banned
            if bad:
                violations.append(f"{py}: importa {bad}")
    assert not violations, "\n".join(violations)
