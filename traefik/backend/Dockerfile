# File: backend/Dockerfile
FROM php:8.3-fpm-alpine

# Install Postgres client libs & enable PDO_PGSQL
RUN apk add --no-cache libpq-dev \
    && docker-php-ext-install pdo_pgsql
