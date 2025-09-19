FROM python:3.11-slim

WORKDIR /app

# Create app user and data directory
RUN useradd -m -r -u 1000 appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Set permissions for app and data directory
RUN chown -R appuser:appuser /app && \
    chmod -R 755 /app/data

# Switch to app user
USER appuser

# Create data directory with correct permissions
RUN mkdir -p /app/data && \
    chmod 755 /app/data

# Expose port
EXPOSE 5000

# Run the parser service
CMD ["python", "app.py"]
