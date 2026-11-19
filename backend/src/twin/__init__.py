import sys

import uvicorn

from twin.settings import Settings


def main() -> None:
    args = sys.argv[1:]
    if args == ["export-openapi"]:
        from twin.adapters.api.openapi import export_openapi
        from twin.bootstrap import create_app

        print(f"Wrote {export_openapi(create_app())}")
        return
    if args:
        raise SystemExit(f"Unknown command: {' '.join(args)}. Try: twin export-openapi")

    settings = Settings()
    # Factory mode, so `--reload` works in development.
    uvicorn.run(
        "twin.bootstrap:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
    )
