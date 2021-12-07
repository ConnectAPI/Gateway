from uvicorn import run

from core.settings import get_settings


def main():
    settings = get_settings()
    run("api:app", host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
