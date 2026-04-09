ARG IMAGE=debian:bookworm-slim

# Stage 1: Build frontend assets (not included in final image)
FROM node:20-slim AS node-builder
WORKDIR /app/assets/admin
COPY app/assets/admin/package*.json ./
RUN npm ci
COPY app/assets/admin ./
RUN npm run build

# Stage 2: Runtime image
FROM $IMAGE

RUN sed -i "s/deb.debian.org/mirror.truenetwork.ru/g" /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get --assume-yes --no-install-recommends install \
        sudo git exim4-base openssh-server \
        unzip mariadb-client iputils-ping cron wget tmux supervisor \
        curl lsb-release ca-certificates \
        python3 python3-pip python3-yaml python3-munch libmemcached-tools python3-pypdf \
        nginx && \
    rm -rf /var/lib/apt/lists/*

COPY --from=docker:dind /usr/local/bin/docker /usr/local/bin/

RUN usermod -s /bin/bash root && \
    adduser --disabled-login -shell /bin/bash dev && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

USER root
WORKDIR /root

# Install PHP 8.1 with extensions, use pecl for timezonedb, then purge build deps
RUN curl -sSLo /tmp/debsuryorg-archive-keyring.deb https://packages.sury.org/debsuryorg-archive-keyring.deb && \
    dpkg -i /tmp/debsuryorg-archive-keyring.deb && \
    echo "deb [signed-by=/usr/share/keyrings/deb.sury.org-php.gpg] https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list && \
    apt-get update && \
    apt-get --assume-yes --no-install-recommends install \
        php8.1 php8.1-zip php8.1-xml php8.1-mbstring php8.1-fpm \
        php8.1-intl php8.1-gd php8.1-xsl php8.1-tidy php8.1-curl php8.1-opcache php8.1-soap \
        php8.1-sqlite3 php8.1-mysql \
        php-pear php8.1-dev make \
        php8.1-imagick imagemagick \
        php8.1-memcached \
        composer && \
    pecl channel-update pecl.php.net && \
    pecl install timezonedb && \
    apt-get --assume-yes purge php8.1-dev php-pear make && \
    apt-get --assume-yes autoremove && \
    rm -rf /var/lib/apt/lists/* /tmp/*

# Install symfony-cli
RUN wget -q https://get.symfony.com/cli/installer -O - | bash && \
    mv /root/.symfony5/bin/symfony /usr/local/bin/symfony && \
    rm -rf /root/.symfony5

COPY pool.conf /etc/php/8.1/fpm/pool.d/pool.conf
COPY php.ini /etc/php/8.1/cli/conf.d/user.ini

RUN echo 'dev ALL=(ALL) NOPASSWD: /webcrate/versions.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/updateprojects.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/updateredirects.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/reload-redirect.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/reload.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/delete.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/backup.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/backup-list.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/backup-save.py' | EDITOR='tee -a' visudo && \
    rm /etc/php/8.1/fpm/pool.d/www.conf

COPY app /app
RUN mkdir /webcrate && \
    chown dev:dev /webcrate && \
    chown -R dev:dev /app

USER dev
WORKDIR /app
RUN rm -f composer.lock && \
    composer install --no-scripts

# Copy only compiled assets (no node_modules/source)
COPY --from=node-builder /app/public/build /app/public/build

USER root
COPY ["init-db.py", "updateprojects.py", "updateredirects.py", "reload-redirect.py", "versions.py", "delete.py", "reload.py", "backup.py", "backup-list.py", "backup-save.py", "supervisord.conf.template", "/webcrate/"]
COPY --from=src log.py /webcrate/
COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod a+rxs \
        /webcrate/init-db.py \
        /webcrate/log.py \
        /webcrate/versions.py \
        /webcrate/updateprojects.py \
        /webcrate/updateredirects.py \
        /webcrate/reload.py \
        /webcrate/delete.py \
        /webcrate/reload-redirect.py \
        /webcrate/backup.py \
        /webcrate/backup-list.py \
        /webcrate/backup-save.py \
        /entrypoint.sh
CMD ["/entrypoint.sh"]
EXPOSE 80
