# ---------- Stage 1: Builder ----------
ARG PYTHON_VERSION=3.11.7
FROM python:${PYTHON_VERSION}-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build deps only here (not in final image)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps into a separate directory
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- Stage 2: Runtime ----------
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Create non-root user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Copy only installed packages from builder
COPY --from=builder /install /usr/local

# Copy app code
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8501

# Healthcheck (important in production)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
CMD python -c "import requests; requests.get('http://localhost:8501')" || exit 1

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]