FROM python:3.12-alpine

ENV APP_HOME=/app

# Install system and build dependencies
RUN apk add --no-cache \
    bash \
    libffi-dev \
    gcc \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    postgresql-dev \
    freetype \
    ttf-dejavu \
    fontconfig \
    libstdc++ \
    libx11 \
    libxext \
    libxrender \
    shadow

# Create non-root user and app directory
RUN addgroup -S packrunner && adduser -S packrunner -G packrunner \
    && mkdir -p $APP_HOME && chown -R packrunner:packrunner $APP_HOME

# Set working directory
WORKDIR $APP_HOME

# Copy dependencies and code
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

# Switch to non-root user
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER packrunner

ENTRYPOINT ["/entrypoint.sh"]
