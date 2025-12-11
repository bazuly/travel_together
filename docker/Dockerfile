FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    nano \
    vim \            
    python3-dev \
    gcc \
    musl-dev \
    libpq-dev \
    nmap && \
    rm -rf /var/lib/apt/lists/* 

RUN pip install uv

WORKDIR /app
COPY .env .env
COPY alembic.ini ./
COPY alembic/ alembic/
COPY pyproject.toml README.md uv.lock ./
COPY app/ app/
COPY ../tests/ tests/

RUN uv venv
ENV PATH="/app/.venv/bin:$PATH"

RUN uv pip install -e ".[dev]"

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]