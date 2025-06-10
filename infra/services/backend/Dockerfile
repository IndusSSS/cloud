# infra/services/backend/Dockerfile

FROM php:8.3-fpm-alpine

WORKDIR /var/www/html

# Copy upload handler into the web root
COPY public/. .

# Ensure www-data owns everything
RUN chown -R www-data:www-data /var/www/html
