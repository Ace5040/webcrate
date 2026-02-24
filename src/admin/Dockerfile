ARG IMAGE=debian:bookworm-slim
FROM $IMAGE

RUN sed -i "s/deb.debian.org/mirror.truenetwork.ru/g" /etc/apt/sources.list.d/debian.sources
RUN apt-get update
RUN apt-get --assume-yes install sudo git nano exim4-base openssh-server \
    unzip mariadb-client mc iputils-ping cron wget tmux supervisor \
    curl lsb-release ca-certificates ruby ruby-dev \
    python3 python3-pip python3-yaml python3-munch libmemcached-tools python3-pypdf \
    nginx

COPY --from=docker:dind /usr/local/bin/docker /usr/local/bin/

RUN usermod -s /bin/bash root

RUN adduser --disabled-login -shell /bin/bash dev && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

USER root
WORKDIR /root

#install php83
RUN curl -sSLo /tmp/debsuryorg-archive-keyring.deb https://packages.sury.org/debsuryorg-archive-keyring.deb && \
    dpkg -i /tmp/debsuryorg-archive-keyring.deb && \
    sh -c 'echo "deb [signed-by=/usr/share/keyrings/deb.sury.org-php.gpg] https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list' && \
    apt-get update
RUN apt-get --assume-yes install php8.1 php8.1-zip php8.1-xml php8.1-mbstring php8.1-fpm \
    php8.1-intl php8.1-gd php8.1-xsl php8.1-tidy php8.1-curl php8.1-opcache php8.1-soap \
    php8.1-sqlite3 php8.1-mysql \
    php-pear php8.1-dev

RUN pecl channel-update pecl.php.net
RUN pecl install timezonedb
RUN apt-get --assume-yes install php8.1-imagick imagemagick
RUN apt-get --assume-yes install php8.1-memcached
RUN apt-get --assume-yes install composer

#install symfony-cli
RUN wget https://get.symfony.com/cli/installer -O - | bash && \
    mv /root/.symfony5/bin/symfony /usr/local/bin/symfony

#misc
COPY pool.conf /etc/php/8.1/fpm/pool.d/pool.conf
COPY php.ini /etc/php/8.1/cli/conf.d/user.ini
RUN echo 'dev ALL=(ALL) NOPASSWD: /webcrate/versions.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/updateprojects.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/updateredirects.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/reload-redirect.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/reload.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/delete.py' | EDITOR='tee -a' visudo && \
    rm /etc/php/8.1/fpm/pool.d/www.conf
COPY app /app
RUN mkdir /webcrate && \
    chown dev:dev /webcrate && \
    chown -R dev:dev /app
USER dev
WORKDIR /app
RUN rm -f composer.lock && \
    composer install --no-scripts
WORKDIR /app/assets/admin

RUN wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
ENV NVM_DIR=/home/dev/.nvm
RUN . $NVM_DIR/nvm.sh && nvm install 16 && nvm use 16

RUN . $NVM_DIR/nvm.sh && npm install --verbose
RUN . $NVM_DIR/nvm.sh && npm run build

USER root
COPY ["init-db.py", "updateprojects.py", "updateredirects.py", "reload-redirect.py", "versions.py", "delete.py", "reload.py", "supervisord.conf.template", "/webcrate/"]
COPY --from=src log.py /webcrate/
COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh
CMD ["/entrypoint.sh"]
RUN chmod a+rxs /webcrate/init-db.py && \
    chmod a+rxs /webcrate/log.py && \
    chmod a+rxs /webcrate/versions.py && \
    chmod a+rxs /webcrate/updateprojects.py && \
    chmod a+rxs /webcrate/updateredirects.py && \
    chmod a+rxs /webcrate/reload.py && \
    chmod a+rxs /webcrate/delete.py && \
    chmod a+rxs /webcrate/reload-redirect.py && \
    chmod a+rxs /entrypoint.sh
EXPOSE 80
