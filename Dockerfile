FROM python:3.11-slim

# Set environment variables
ENV TIME_ZONE=$TIME_ZONE \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PATH="/root/.local/bin:$PATH"

# Install OS dependencies
RUN apt-get update && apt-get install -y \
  net-tools \
  netcat-traditional \
  build-essential \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app code
ADD billsec_portal .

# Add entrypoint for waiting on DB
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Run the entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]