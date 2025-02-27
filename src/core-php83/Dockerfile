ARG IMAGE=debian-slim
FROM $IMAGE

RUN sed -i "s/deb.debian.org/mirror.truenetwork.ru/g" /etc/apt/sources.list.d/debian.sources
RUN apt-get update
RUN apt-get --assume-yes install sudo git nano exim4-base openssh-server \
    unzip mariadb-client mc iputils-ping cron wget tmux supervisor \
    curl lsb-release ca-certificates ruby ruby-dev \
    python3 python3-pip python3-yaml python3-munch libmemcached-tools python3-pypdf

RUN usermod -s /bin/bash root

RUN adduser --no-create-home --disabled-login -shell /bin/bash dev && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

USER root
WORKDIR /root

# php83-fileinfo php83-ctype php83-xmlreader php83-xmlwriter php83-openssl
# php83-simplexml php83-phar php83-tokenizer php83-iconv php83-pdo
# php83-pdo_sqlite  php83-pdo_mysql php83-mysqli

#install php83
RUN curl -sSLo /tmp/debsuryorg-archive-keyring.deb https://packages.sury.su/debsuryorg-archive-keyring.deb && \
    dpkg -i /tmp/debsuryorg-archive-keyring.deb && \
    sh -c 'echo "deb [signed-by=/usr/share/keyrings/deb.sury.org-php.gpg] https://packages.sury.su/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list' && \
    apt-get update
RUN apt-get --assume-yes install php8.3 php8.3-zip php8.3-xml php8.3-mbstring php8.3-fpm \
    php8.3-intl php8.3-gd php8.3-xsl php8.3-tidy php8.3-curl php8.3-opcache php8.3-soap \
    php8.3-sqlite3 php8.3-mysql \
    php-pear php8.3-dev

RUN pecl channel-update pecl.php.net
RUN pecl install timezonedb
RUN apt-get --assume-yes install php8.3-imagick imagemagick
RUN apt-get --assume-yes install php8.3-memcached
RUN apt-get --assume-yes install composer

#install ioncube
RUN wget https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz && \
    tar xzf ioncube_loaders_lin_x86-64.tar.gz && \
    cp ./ioncube/ioncube_loader_lin_8.3.so $(php-config --extension-dir)/ioncube_loader_lin.so && \
    rm -rf /root/ioncube && \
    rm -f /root/ioncube_loaders_lin_x86-64.tar.gz

RUN wget -O drush.phar https://github.com/drush-ops/drush-launcher/releases/latest/download/drush.phar && \
    chmod +x drush.phar && \
    mv drush.phar /usr/bin/drush && \
    ssh-keygen -A

#install compass
RUN gem install compass

#install oh-my-bash
RUN apt-get --assume-yes install gawk
RUN wget https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh && \
    chmod u+x install.sh && \
    ./install.sh --prefix=/usr

#install ble.sh
RUN git clone --recursive --depth 1 --shallow-submodules https://github.com/akinomyoga/ble.sh.git && \
    make -C ble.sh install PREFIX=/usr

#install symfony-cli
RUN wget https://get.symfony.com/cli/installer -O - | bash && \
    mv /root/.symfony5/bin/symfony /usr/local/bin/symfony

#misc config
RUN sed -i "s/;process_control_timeout = 0/process_control_timeout = 10s/g" /etc/php/8.3/fpm/php-fpm.conf && \
    sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/g" /etc/ssh/sshd_config && \
    sed -i "s/#PasswordAuthentication yes/PasswordAuthentication yes/g" /etc/ssh/sshd_config && \
    sed -i "s/#StrictModes yes/StrictModes no/g" /etc/ssh/sshd_config && \
    sed -i "s/PrintMotd no/PrintMotd yes/g" /etc/ssh/sshd_config && \
    cat > /etc/motd && \
    rm /etc/update-motd.d/10-uname && \
    rm /etc/php/8.3/fpm/pool.d/www.conf && \
    mkdir -p /webcrate && \
    chmod o-rwx /webcrate

WORKDIR /
COPY ["versions.py", "parse-projects.py", "sync_ssh_keys.sh", "log.py", "supervisord.conf.template", "supervisord-user.conf.template", "/webcrate/"]
COPY bashrc.sh /etc/bashrc.sh
COPY ["entrypoint.sh", "/"]
RUN chmod u+x /webcrate/sync_ssh_keys.sh && \
    chmod u+x /webcrate/parse-projects.py && \
    chmod u+x /webcrate/versions.py && \
    chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
EXPOSE 22 9000
