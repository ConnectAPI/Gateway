import uvicorn


def main():
    uvicorn.run("api:api", host="0.0.0.0", port=80)


if __name__ == "__main__":
    main()
