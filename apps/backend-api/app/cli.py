"""
Command-line entry points for running the backend API service.
"""

from __future__ import annotations

import argparse
import os
from typing import Sequence

import uvicorn


DEFAULT_APP_IMPORT = "app.main:app"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="telemetry-backend",
        description="Run the telemetry backend API service.",
    )
    parser.add_argument(
        "--app",
        default=os.getenv("TELEMETRY_BACKEND_APP", DEFAULT_APP_IMPORT),
        help="ASGI app import path (default: app.main:app).",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("HOST", "0.0.0.0"),
        help="Bind host (default: 0.0.0.0).",
    )
    parser.add_argument(
        "--port",
        default=int(os.getenv("PORT", "8000")),
        type=int,
        help="Bind port (default: 8000).",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("LOG_LEVEL", "info").lower(),
        choices=[
            "critical",
            "error",
            "warning",
            "info",
            "debug",
            "trace",
        ],
        help="Uvicorn log level.",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development.",
    )
    return parser


def run(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    uvicorn.run(
        args.app,
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        reload=args.reload,
    )


def main() -> None:
    run()


def dev_main() -> None:
    run(["--reload"])
