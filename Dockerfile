# FROM mich43l/alpine

# LABEL architecture="x86_64"                        \
#       build-date="$BUILD_DATE"                     \
#       license="MIT"                                \
#       name="mich43l/billsec_portal"                \
#       summary="Billsec portal for SIP CDR report"  \
#       vcs-type="git"                               \
#       vcs-url="https://github.com/mach1el/billsec-portal"

# RUN apk add py3-django py3-psycopg2 py3-dotenv --no-cache && rm -rf /var/cache/apk/*

# ADD . $USER_HOME

# WORKDIR $USER_HOME/billsec_portal

# RUN python manage.py makemigrations
# RUN python manage.py migrate

# ENV DB_NAME \
#   DB_USER \
#   DB_PASSWORD \
#   DB_HOST=localhost \
#   DB_PORT=5432 \
#   DC_DB_NAME \
#   DC_DB_USER \
#   DC_DB_PASSWORD \
#   DC_DB_HOST=localhost \
#   DC_DB_PORT=5432

# EXPOSE 8000

# ADD units /
# RUN chmod +x /etc/service/*/*

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/root/.local/bin:$PATH"

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