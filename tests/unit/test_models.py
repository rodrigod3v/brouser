from brouser.domain.models import Action, ActionKind, ElementNode, Snapshot


def test_parse_loose_json_puro():
    a = Action.parse_loose('{"kind": "click", "index": 3, "reason": "abrir"}')
    assert a.kind == ActionKind.CLICK
    assert a.index == 3


def test_parse_loose_com_fence():
    raw = 'Claro!\n```json\n{"action": "goto", "url": "https://x.com"}\n```'
    a = Action.parse_loose(raw)
    assert a.kind == ActionKind.GOTO
    assert a.url == "https://x.com"


def test_parse_loose_com_texto_em_volta():
    a = Action.parse_loose('vou clicar {"kind": "done", "answer": "42"} fim')
    assert a.kind == ActionKind.DONE
    assert a.answer == "42"


def test_parse_loose_invalido():
    import pytest

    with pytest.raises(ValueError):
        Action.parse_loose("sem json aqui")


def test_snapshot_render_respeita_limite():
    snap = Snapshot(
        url="https://x",
        elements=[ElementNode(index=i, tag="a", text=f"el{i}") for i in range(10)],
    )
    out = snap.render(max_elements=3)
    assert "[2]" in out
    assert "[3]" not in out
