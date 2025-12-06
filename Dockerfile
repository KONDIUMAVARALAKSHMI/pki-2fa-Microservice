############### BUILDER ################
FROM python:3.11-slim AS builder

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

############### RUNTIME ################
FROM python:3.11-slim

WORKDIR /app
ENV TZ=UTC

# Install cron + timezone data
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app /app/app
COPY scripts /app/scripts
COPY cron/2fa-cron /etc/cron.d/2fa-cron
COPY student_private.pem /app/student_private.pem
COPY student_public.pem /app/student_public.pem
COPY instructor_public.pem /app/instructor_public.pem

# Set permissions for cron
RUN chmod 0644 /etc/cron.d/2fa-cron && crontab /etc/cron.d/2fa-cron

# Create persistent directories
RUN mkdir -p /data /cron && chmod -R 755 /data /cron

EXPOSE 8080

# Run cron in background and start server
CMD service cron start && uvicorn app.main:app --host 0.0.0.0 --port 8080
