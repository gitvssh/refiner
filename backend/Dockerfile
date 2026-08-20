FROM python:3.14-slim@sha256:ce40764625a4ff50df3548277632e7f96c4e77fe75fa848aae9885476e7df5a4 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN python -m pip install --no-cache-dir uv==0.9.26

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY backend ./backend
RUN uv sync --frozen --no-dev

USER 65532:65532
EXPOSE 8000
CMD ["/app/.venv/bin/uvicorn", "refiner.interfaces.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
