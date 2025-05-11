FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY alembic.ini ./alembic.ini
COPY web ./web
COPY database ./database
COPY migration ./migration

CMD ["python", "web/app.py"]