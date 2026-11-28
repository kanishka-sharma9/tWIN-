import sys

import uvicorn
from pydantic import SecretStr

from twin.settings import Settings


def main() -> None:
    args = sys.argv[1:]
    if args == ["export-openapi"]:
        from twin.adapters.api.openapi import export_openapi
        from twin.bootstrap import create_app

        # The schema does not depend on the secret, so exporting needs none configured.
        settings = Settings(
            jwt_secret=SecretStr("openapi-export-only-placeholder-secret")
        )
        print(f"Wrote {export_openapi(create_app(settings))}")
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
