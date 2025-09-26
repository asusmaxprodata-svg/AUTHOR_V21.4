# KANG_BOT Dockerfile - Enhanced with error handling
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/reports /app/models

# Set permissions
RUN chmod +x /app/entrypoint.sh

# Health check - Enhanced for deployment with fallbacks
HEALTHCHECK --interval=90s --timeout=15s --start-period=180s --retries=5 \
  CMD python -c "import sys; sys.path.append('.'); \
try: \
    from core.import_fixes import get_logger; \
    logger = get_logger('healthcheck'); \
except: \
    import logging; \
    logger = logging.getLogger('healthcheck'); \
try: \
    from core.health_check import get_health_status; \
    health = get_health_status(); \
    status = health.get('overall_status', 'unknown'); \
    logger.info(f'Status kesehatan: {status}'); \
    print('healthy' if status in ['healthy', 'warning'] else 'unhealthy'); \
except Exception as e: \
    logger.error(f'Pemeriksaan kesehatan gagal: {e}'); \
    print('unhealthy')"

# Use entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["python", "run.py"]
