ARG IMAGE=debian:bookworm-slim
FROM $IMAGE

RUN sed -i "s/deb.debian.org/mirror.truenetwork.ru/g" /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get --assume-yes --no-install-recommends install \
        sudo git exim4-base openssh-server \
        unzip mariadb-client iputils-ping cron wget tmux supervisor \
        curl lsb-release ca-certificates ruby ruby-dev make gawk \
        python3 python3-pip python3-yaml python3-munch libmemcached-tools python3-pypdf \
        python-is-python3 && \
    rm -rf /var/lib/apt/lists/*

RUN usermod -s /bin/bash root && \
    adduser --no-create-home --disabled-login -shell /bin/bash dev && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

USER root
WORKDIR /root

# Install PHP 7.4 with extensions, compass (while gcc available), then purge build deps
RUN curl -sSLo /tmp/debsuryorg-archive-keyring.deb https://packages.sury.org/debsuryorg-archive-keyring.deb && \
    dpkg -i /tmp/debsuryorg-archive-keyring.deb && \
    echo "deb [signed-by=/usr/share/keyrings/deb.sury.org-php.gpg] https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list && \
    apt-get update && \
    apt-get --assume-yes --no-install-recommends install \
        php7.4 php7.4-zip php7.4-xml php7.4-mbstring php7.4-fpm \
        php7.4-intl php7.4-gd php7.4-xsl php7.4-tidy php7.4-curl php7.4-opcache php7.4-soap \
        php7.4-sqlite3 php7.4-mysql \
        php-pear php7.4-dev \
        php7.4-imagick imagemagick \
        php7.4-memcached \
        libffi-dev && \
    pecl channel-update pecl.php.net && \
    pecl install timezonedb && \
    gem install compass --no-document && \
    gem cleanup && \
    apt-get --assume-yes purge php7.4-dev php-pear libffi-dev && \
    apt-get --assume-yes autoremove && \
    rm -rf /var/lib/apt/lists/* /tmp/*

# Install composer
RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" && \
    php composer-setup.php --2.2 --install-dir=/usr/local/bin --filename=composer && \
    rm composer-setup.php

# Install ioncube
RUN wget -q https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz && \
    tar xzf ioncube_loaders_lin_x86-64.tar.gz && \
    cp ./ioncube/ioncube_loader_lin_7.4.so $(php-config --extension-dir)/ioncube_loader_lin.so && \
    rm -rf /root/ioncube /root/ioncube_loaders_lin_x86-64.tar.gz

# Install drush + generate SSH host keys
RUN wget -qO /usr/bin/drush https://github.com/drush-ops/drush-launcher/releases/latest/download/drush.phar && \
    chmod +x /usr/bin/drush && \
    ssh-keygen -A

# Install oh-my-bash
RUN wget -q https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh && \
    chmod u+x install.sh && \
    ./install.sh --prefix=/usr && \
    rm install.sh

# Install ble.sh
RUN git clone --recursive --depth 1 --shallow-submodules https://github.com/akinomyoga/ble.sh.git && \
    make -C ble.sh install PREFIX=/usr && \
    rm -rf ble.sh

# Install symfony-cli
RUN wget -q https://get.symfony.com/cli/installer -O - | bash && \
    mv /root/.symfony5/bin/symfony /usr/local/bin/symfony && \
    rm -rf /root/.symfony5

# Install mise
RUN curl -q https://mise.run | MISE_INSTALL_PATH=/usr/local/bin/mise sh

# Misc config
RUN sed -i "s/;process_control_timeout = 0/process_control_timeout = 10s/g" /etc/php/7.4/fpm/php-fpm.conf && \
    sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/g" /etc/ssh/sshd_config && \
    sed -i "s/#PasswordAuthentication yes/PasswordAuthentication yes/g" /etc/ssh/sshd_config && \
    sed -i "s/#StrictModes yes/StrictModes no/g" /etc/ssh/sshd_config && \
    sed -i "s/PrintMotd no/PrintMotd yes/g" /etc/ssh/sshd_config && \
    cat > /etc/motd && \
    rm /etc/update-motd.d/10-uname && \
    rm /etc/php/7.4/fpm/pool.d/www.conf && \
    mkdir -p /webcrate && \
    chmod o-rwx /webcrate

WORKDIR /
COPY ["versions.py", "parse-projects.py", "sync_ssh_keys.sh", "supervisord.conf.template", "supervisord-user.conf.template", "/webcrate/"]
COPY --from=src log.py /webcrate/
COPY bashrc.sh /etc/bashrc.sh
COPY ["entrypoint.sh", "/"]
RUN chmod u+x \
        /webcrate/sync_ssh_keys.sh \
        /webcrate/parse-projects.py \
        /webcrate/versions.py \
        /entrypoint.sh
CMD ["/entrypoint.sh"]
EXPOSE 22 9000
