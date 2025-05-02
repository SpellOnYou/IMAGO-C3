FROM python:3.11-slim

WORKDIR /backend

COPY pyproject.toml poetry.lock* /backend/
RUN pip install poetry && poetry install

COPY app /backend/app
COPY tests /backend/tests
COPY .env .env
ENV PYTHONPATH=/backend

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
