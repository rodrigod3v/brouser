import pytest

from brouser.config import ModelRouting, Settings
from brouser.llm.router import ModelRouter


def _settings(**kw) -> Settings:
    base = {
        "llm_base_url": "https://paid",
        "llm_api_key": "k",
        "llm_model": "paid-model",
        "llm_free_base_url": "https://free",
        "llm_free_api_key": "k",
        "llm_free_model": "free-model",
    }
    base.update(kw)
    return Settings.model_validate(base)


def test_auto_prefere_free_quando_configurado():
    r = ModelRouter(_settings(model_routing=ModelRouting.AUTO))
    assert r.current().model_name == "free-model"


def test_auto_cai_no_paid_sem_free():
    s = _settings(
        model_routing=ModelRouting.AUTO,
        llm_free_base_url="",
        llm_free_api_key="",
        llm_free_model="",
    )
    assert ModelRouter(s).current().model_name == "paid-model"


def test_paid_forcado():
    r = ModelRouter(_settings(model_routing=ModelRouting.PAID))
    assert r.current().model_name == "paid-model"


def test_free_sem_config_erro():
    s = _settings(
        model_routing=ModelRouting.FREE,
        llm_free_base_url="",
        llm_free_api_key="",
        llm_free_model="",
    )
    with pytest.raises(RuntimeError, match="tier free"):
        ModelRouter(s).current()


def test_escalate_promove_paid():
    r = ModelRouter(_settings(model_routing=ModelRouting.AUTO))
    assert r.current().model_name == "free-model"
    r.escalate()
    assert r.current().model_name == "paid-model"
