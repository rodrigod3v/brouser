from brouser.domain.models import Action, ActionKind, Step, TaskResult
from brouser.memory.obsidian import ObsidianMemory


def _result() -> TaskResult:
    r = TaskResult(task="Pesquisar preco do RTX 5090!", model="m")
    r.steps.append(Step(n=1, action=Action(kind=ActionKind.GOTO, url="https://google.com")))
    r.finish(True, "top 3: a, b, c")
    return r


async def test_save_session_cria_nota(tmp_path):
    mem = ObsidianMemory(tmp_path)
    path = await mem.save_session(_result())
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "status: success" in content
    assert "RTX 5090" in content
    assert "| 1 | goto |" in content
    assert "sessions" in str(path)


def test_slug_sanitiza():
    assert ObsidianMemory._slug("Ola Mundo!!! teste") == "ola-mundo-teste"
    assert ObsidianMemory._slug("!!!") == "task"
