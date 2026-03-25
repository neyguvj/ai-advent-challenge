FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/

WORKDIR /app

COPY pyproject.toml .
RUN uv sync

FROM python:3.12-slim
RUN apt-get update && apt-get install curl -y

COPY --from=builder /app/.venv /app/.venv
COPY app app
COPY migrations migrations
COPY alembic.ini .

RUN chmod +x /app/entrypoint.sh

ENV VIRTUAL_ENV=/app/.venv 
ENV PATH="/app/.venv/bin:$PATH" 

EXPOSE 8080

CMD ["/app/entrypoint.sh"]