# Generic image for static / self-contained PHP benchmark targets that ship
# PHP source but no Dockerfile of their own. Build context is the target dir.
# Serves on port 80 via Apache + mod_php.
#
# Note: targets that need a database (e.g. MySQL/MariaDB) will not be fully
# functional from this single image -- those ship their own compose file and
# are run through it instead. This template covers self-contained PHP apps.
FROM php:8.2-apache

# Common extensions used by the PHP targets in this repo.
RUN docker-php-ext-install mysqli pdo pdo_mysql 2>/dev/null || true

COPY . /var/www/html/
RUN chown -R www-data:www-data /var/www/html

EXPOSE 80
