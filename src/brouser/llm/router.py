"""ModelRouter — Strategy para selecao free/paid/auto."""

from __future__ import annotations

from brouser.config import ModelRouting, Settings
from brouser.llm.client import OpenAICompatibleLLM


class ModelRouter:
    """Resolve qual LLM usar conforme tier configurado.

    auto: free se configurado, senao paid. Escalacao manual via switch_to_paid().
    """

    def __init__(self, settings: Settings) -> None:
        self._s = settings
        self._escalated = False

    def current(self) -> OpenAICompatibleLLM:
        s = self._s
        if s.model_routing == ModelRouting.FREE:
            if not s.free_tier_configured:
                msg = "MODEL_ROUTING=free mas tier free nao configurado no .env"
                raise RuntimeError(msg)
            return self._free()
        if s.model_routing == ModelRouting.PAID or self._escalated or not s.free_tier_configured:
            return self._paid()
        return self._free()

    def _free(self) -> OpenAICompatibleLLM:
        s = self._s
        return OpenAICompatibleLLM(
            s.llm_free_base_url, s.llm_free_api_key, s.llm_free_model, s.brouser_max_elements
        )

    def _paid(self) -> OpenAICompatibleLLM:
        s = self._s
        return OpenAICompatibleLLM(
            s.llm_base_url, s.llm_api_key, s.llm_model, s.brouser_max_elements
        )

    def escalate(self) -> None:
        """Promove para tier pago (ex.: modelo free estagnou)."""
        self._escalated = True

    @property
    def escalated(self) -> bool:
        return self._escalated
