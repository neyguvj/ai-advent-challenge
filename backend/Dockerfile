FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/

WORKDIR /backend

COPY pyproject.toml .
RUN uv sync

FROM python:3.12-slim
COPY --from=builder /backend/.venv /backend/.venv
COPY app.py backend/

ENV VIRTUAL_ENV=/backend/.venv 
ENV PATH="/backend/.venv/bin:$PATH" 

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "4", "backend.app:app"]