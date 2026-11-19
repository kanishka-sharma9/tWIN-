import pytest
from pydantic_settings import SettingsConfigDict

from twin import main
from twin.settings import Settings


class NoFileSettings(Settings):
    """Settings that ignore any .env file, so the developer's own file cannot change a test."""

    model_config = SettingsConfigDict(env_file=None)


def test_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TWIN_HOST", raising=False)
    monkeypatch.delenv("TWIN_PORT", raising=False)
    settings = NoFileSettings()
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000


def test_port_is_read_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TWIN_PORT", "9001")
    assert NoFileSettings().port == 9001


def test_main_starts_uvicorn_in_factory_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TWIN_PORT", "9002")
    monkeypatch.setattr("sys.argv", ["twin"])
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    monkeypatch.setattr("uvicorn.run", lambda *a, **k: calls.append((a, k)))
    main()
    args, kwargs = calls[0]
    assert args == ("twin.bootstrap:create_app",)
    assert kwargs["factory"] is True
    assert kwargs["port"] == 9002


def test_main_rejects_an_unknown_command(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["twin", "nope"])
    with pytest.raises(SystemExit, match="Unknown command"):
        main()
