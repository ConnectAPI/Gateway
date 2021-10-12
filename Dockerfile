FROM python:3.10-slim-buster

COPY . .

RUN pip install -r requirements.txt --no-cache-dir

EXPOSE 1687 80

ENV PYTHONPATH "${PYTHONPATH}:./src"

CMD ["python", "-m", "src"]
