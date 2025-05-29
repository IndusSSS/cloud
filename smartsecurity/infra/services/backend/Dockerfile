# services/backend/Dockerfile

FROM php:8.3-fpm-alpine

# Install minimal extensions you need (none for now)
# RUN docker-php-ext-install pdo_mysql

WORKDIR /var/www/html
COPY public/ .    # upload.php lives here

# Permissions
RUN chown -R www-data:www-data /var/www/html
