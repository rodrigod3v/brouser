"""PlaywrightBrowser — adapter do port Browser."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from brouser.browser.dom import JS_EXTRACT, parse_elements
from brouser.config import Settings
from brouser.domain.models import Snapshot

if TYPE_CHECKING:
    from playwright.async_api import BrowserContext, Page, Playwright

IDX_ATTR = "data-brouser-idx"


class PlaywrightBrowser:
    """Controla Chromium via Playwright com perfil persistente."""

    def __init__(self, settings: Settings) -> None:
        self._s = settings
        self._pw: Playwright | None = None
        self._ctx: BrowserContext | None = None
        self._page: Page | None = None

    async def __aenter__(self) -> Self:
        from playwright.async_api import async_playwright

        self._pw = await async_playwright().start()
        channel = None if self._s.brouser_channel == "chromium" else self._s.brouser_channel
        self._ctx = await self._pw.chromium.launch_persistent_context(
            user_data_dir=self._s.brouser_profile_dir,
            headless=self._s.brouser_headless,
            channel=channel,
            viewport={"width": 1280, "height": 900},
        )
        self._page = self._ctx.pages[0] if self._ctx.pages else await self._ctx.new_page()
        self._page.set_default_timeout(self._s.brouser_nav_timeout_ms)
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    def _p(self) -> Page:
        if self._page is None:
            msg = "Browser nao iniciado — use 'async with PlaywrightBrowser(...)'"
            raise RuntimeError(msg)
        return self._page

    async def goto(self, url: str) -> None:
        await self._p().goto(url, wait_until="domcontentloaded")

    async def snapshot(self) -> Snapshot:
        page = self._p()
        raw = await page.evaluate(JS_EXTRACT)
        return Snapshot(
            url=page.url,
            title=await page.title(),
            elements=parse_elements(raw),
        )

    async def click(self, index: int) -> None:
        await self._p().locator(f"[{IDX_ATTR}='{index}']").first.click(timeout=5000)

    async def type_text(self, index: int, text: str) -> None:
        loc = self._p().locator(f"[{IDX_ATTR}='{index}']").first
        await loc.click(timeout=5000)
        await loc.fill(text, timeout=5000)

    async def scroll(self, dy: int) -> None:
        await self._p().mouse.wheel(0, dy)

    async def back(self) -> None:
        await self._p().go_back(wait_until="domcontentloaded")

    async def wait(self, ms: int) -> None:
        await self._p().wait_for_timeout(ms)

    async def page_text(self) -> str:
        return (await self._p().inner_text("body"))[:8000]

    async def close(self) -> None:
        if self._ctx is not None:
            await self._ctx.close()
            self._ctx = None
        if self._pw is not None:
            await self._pw.stop()
            self._pw = None
