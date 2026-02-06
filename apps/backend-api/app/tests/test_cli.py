from __future__ import annotations

from app import cli


def test_build_parser_uses_env_default(monkeypatch):
    monkeypatch.setenv("TELEMETRY_BACKEND_APP", "app.main:create_app")

    parser = cli.build_parser()
    args = parser.parse_args([])

    assert args.app == "app.main:create_app"


def test_run_invokes_uvicorn(monkeypatch):
    captured = {}

    def fake_run(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs

    monkeypatch.setattr(cli.uvicorn, "run", fake_run)

    cli.run(
        [
            "--host",
            "127.0.0.1",
            "--port",
            "9001",
            "--log-level",
            "debug",
        ]
    )

    assert captured["args"] == ("app.main:app",)
    assert captured["kwargs"]["host"] == "127.0.0.1"
    assert captured["kwargs"]["port"] == 9001
    assert captured["kwargs"]["log_level"] == "debug"
    assert captured["kwargs"]["reload"] is False


def test_dev_main_enables_reload(monkeypatch):
    captured = {}

    def fake_run(*args, **kwargs):
        captured["kwargs"] = kwargs

    monkeypatch.setattr(cli.uvicorn, "run", fake_run)

    cli.dev_main()

    assert captured["kwargs"]["reload"] is True
