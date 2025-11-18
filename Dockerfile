FROM python:3.12-slim

# Set working directory
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirments first for caching
COPY feedback_app/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy app source
COPY . /app

# Create data and logs directories
RUN mkdir -p /app/data /app/logs && chown -R 1000:1000 /app

USER 1000

EXPOSE 5001

VOLUME ["/app/data", "/app/logs"]

CMD ["sh", "-c", "python feedback_app/setup.py && python feedback_app/app.py"]
