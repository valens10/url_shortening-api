# Use Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SECRET_KEY="django-insecure-temporary-key-for-build-only"

# Set working directory
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project files
COPY . .

# Create media directory and set permissions
RUN mkdir -p /usr/src/app/media && chmod -R 777 /usr/src/app/media

# Collect static files
RUN python manage.py collectstatic --noinput

# Create a script to run migrations and start the server
RUN echo '#!/bin/bash\npython manage.py migrate\nexec gunicorn --bind 0.0.0.0:8000 --workers=3 --timeout=120 url_shortener.wsgi:application' > /usr/src/app/start.sh
RUN chmod +x /usr/src/app/start.sh

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Run the start script
CMD ["/usr/src/app/start.sh"]
