import uvicorn

from twin.settings import Settings


def main() -> None:
    settings = Settings()
    # Factory mode, so `--reload` works in development.
    uvicorn.run(
        "twin.bootstrap:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
    )
