FROM python:3.10-slim-buster

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY ./src ./src

EXPOSE 80 1687

ENV PYTHONPATH "${PYTHONPATH}:./src"
ENV ENV "producation"
ENV HOST "0.0.0.0"
ENV PORT 80


WORKDIR ./src

CMD ["python", "run.py"]
