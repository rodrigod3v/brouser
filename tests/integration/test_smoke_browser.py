"""Smoke: abre browser de verdade. Roda so com: pytest -m integration."""

import pytest

from brouser.browser.controller import PlaywrightBrowser
from brouser.config import Settings

pytestmark = pytest.mark.integration


async def test_browser_abre_e_extrai_elementos(tmp_path):
    settings = Settings(
        brouser_headless=True,
        brouser_profile_dir=str(tmp_path / "prof"),
        llm_api_key="x",
    )
    async with PlaywrightBrowser(settings) as b:
        await b.goto("https://example.com")
        snap = await b.snapshot()
        assert "example" in snap.url
        assert await b.page_text() != ""
