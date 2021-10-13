from uvicorn import run


def main():
    run("api_entry:api", host="0.0.0.0", port=80)


if __name__ == "__main__":
    main()
