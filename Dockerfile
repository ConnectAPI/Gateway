FROM python:3.10-buster

COPY . .

RUN pip install -r --no-cache-dir requirements.txt

EXPOSE 1687 80

CMD ["python", "-m", "src"]
