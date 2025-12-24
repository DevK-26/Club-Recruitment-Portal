FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . .

# Run migrations and start app
CMD python -m flask db upgrade && gunicorn --bind 0.0.0.0:$PORT --workers 2 run:app
