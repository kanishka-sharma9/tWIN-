import sys

import uvicorn
from pydantic import SecretStr

from twin.settings import Settings

USAGE = """Usage: twin [command]

  twin                      Start the API server (TWIN_HOST:TWIN_PORT)
  twin export-openapi       Write the OpenAPI schema for the web client
  twin set-password <email> Reset a forgotten password; reads it from a prompt,
                            or one line on standard input"""


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
    if args in (["--help"], ["-h"]):
        print(USAGE)
        return
    if args[:1] == ["set-password"]:
        from twin.adapters.cli import set_password
        from twin.bootstrap import create_reset_password

        set_password(args[1:], create_reset_password)
        return
    if args:
        raise SystemExit(
            f"Unknown command: {' '.join(args)}. "
            "Try: twin export-openapi, twin set-password <email>"
        )

    settings = Settings()
    # Factory mode, so `--reload` works in development.
    uvicorn.run(
        "twin.bootstrap:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
    )
