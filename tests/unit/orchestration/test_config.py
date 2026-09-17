import os

from quantlab.orchestration.config import ControlPlaneConfig


def test_secret_presence_is_boolean(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "secret-value")
    cfg = ControlPlaneConfig.from_environment("C:/QUANT_LAB")
    status = cfg.secret_status()
    assert status["OPENAI_API_KEY"] is True
    assert "secret-value" not in repr(status)


def test_missing_secret_is_false(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    cfg = ControlPlaneConfig.from_environment("C:/QUANT_LAB")
    assert cfg.secret_status()["ANTHROPIC_API_KEY"] is False


def test_root_is_normalized(monkeypatch) -> None:
    cfg = ControlPlaneConfig.from_environment("C:/Quant_Lab")
    assert cfg.project_root.name.lower() == "quant_lab"


def test_gdrive_root_is_configurable(monkeypatch) -> None:
    monkeypatch.setenv("QUANTLAB_GDRIVE_ROOT", "Quant_Lab")
    cfg = ControlPlaneConfig.from_environment("C:/QUANT_LAB")
    assert cfg.gdrive_root == "Quant_Lab"


def test_allowed_secret_names_are_fixed(monkeypatch) -> None:
    monkeypatch.setenv("RANDOM_SECRET", "x")
    cfg = ControlPlaneConfig.from_environment("C:/QUANT_LAB")
    assert "RANDOM_SECRET" not in cfg.secret_status()
