# ---------- Stage 1: install dependencies ----------
FROM python:3.14-slim AS builder

WORKDIR /build

# Create a virtual environment to hold the dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the requirements first, so this layer is cached
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ---------- Stage 2: the final, minimal image ----------
FROM python:3.14-slim

# Don't write .pyc files; send logs straight to the terminal
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Create a non-root user to run the app
RUN useradd --create-home --uid 10001 appuser

WORKDIR /home/appuser

# Copy the installed dependencies from the builder stage, then the app code
COPY --from=builder /opt/venv /opt/venv
COPY app/ ./app/

# From here on, everything runs as appuser, not root
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]