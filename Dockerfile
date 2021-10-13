FROM python:3.10-slim-buster

COPY . .

RUN pip install -r requirements.txt --no-cache-dir

EXPOSE 80 1687

ENV PYTHONPATH "${PYTHONPATH}:./src"

CMD ["python", "-m", "src"]
