FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Make build script executable
RUN chmod +x build.sh

# Run migrations
RUN python -m flask db upgrade || echo "Migrations will run on start"

# Expose port
EXPOSE 8080

# Start application
CMD gunicorn --bind 0.0.0.0:8080 --workers 2 run:app
