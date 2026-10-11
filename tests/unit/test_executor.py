import pytest

from brouser.actions.executor import ActionExecutor
from brouser.domain.models import Action, ActionKind, Snapshot


class FakeBrowser:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    async def goto(self, url):
        self.calls.append(("goto", url))

    async def snapshot(self):
        return Snapshot(url="x")

    async def click(self, index):
        self.calls.append(("click", index))

    async def type_text(self, index, text):
        self.calls.append(("type", index, text))

    async def scroll(self, dy):
        self.calls.append(("scroll", dy))

    async def back(self):
        self.calls.append(("back",))

    async def wait(self, ms):
        self.calls.append(("wait", ms))

    async def page_text(self):
        return "txt"

    async def close(self):
        pass


async def test_executor_click():
    b = FakeBrowser()
    await ActionExecutor(b).execute(Action(kind=ActionKind.CLICK, index=7))
    assert b.calls == [("click", 7)]


async def test_executor_type_sem_index_erro():
    with pytest.raises(ValueError, match="exige index"):
        await ActionExecutor(FakeBrowser()).execute(Action(kind=ActionKind.TYPE, text="x"))


async def test_executor_goto_sem_url_erro():
    with pytest.raises(ValueError, match="exige url"):
        await ActionExecutor(FakeBrowser()).execute(Action(kind=ActionKind.GOTO))


async def test_executor_done_noop():
    b = FakeBrowser()
    await ActionExecutor(b).execute(Action(kind=ActionKind.DONE, answer="fim"))
    assert b.calls == []
