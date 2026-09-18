FROM php:7.4-apache

RUN docker-php-ext-install mysqli pdo pdo_mysql \
    && a2enmod rewrite

COPY . /var/www/html/
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 777 /var/www/html/img/uploads || true

EXPOSE 80
