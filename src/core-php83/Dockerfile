ARG IMAGE_ALPINE_321_BASE
FROM $IMAGE_ALPINE_321_BASE

RUN apk update && apk add --no-cache sudo git nano exim openssh unzip mariadb-client mc iputils cronie wget tmux py3-pip python3 py3-yaml py3-munch libmemcached supervisor shadow

RUN chsh -s /bin/bash root

RUN adduser -D -s /bin/bash dev && \
    echo 'dev:dev' | chpasswd && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

USER root
WORKDIR /root

#install php83
RUN apk add --no-cache php83 php83-fileinfo php83-ctype php83-pear php83-zip php83-xmlreader php83-xmlwriter php83-mbstring php83-openssl php83-xml php83-fpm php83-intl php83-gd php83-xsl php83-simplexml php83-phar php83-tidy php83-tokenizer php83-curl php83-opcache php83-iconv php83-pdo php83-soap
RUN apk add --no-cache php83-pdo_sqlite php83-sqlite3 php83-pdo_mysql php83-mysqli php83-pecl-imagick
RUN apk add --no-cache php83-pecl-timezonedb php83-pecl-memcached
RUN apk add --no-cache composer ruby py3-setuptools py3-munch py3-pypdf bash make curl

#install ioncube
RUN wget https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz && \
    tar xzf ioncube_loaders_lin_x86-64.tar.gz && \
    cp ./ioncube/ioncube_loader_lin_8.3.so /usr/lib/php83/modules/ioncube_loader_lin.so && \
    rm -rf /root/ioncube && \
    rm -f /root/ioncube_loaders_lin_x86-64.tar.gz

RUN wget -O drush.phar https://github.com/drush-ops/drush-launcher/releases/latest/download/drush.phar && \
    chmod +x drush.phar && \
    mv drush.phar /usr/bin/drush && \
    gem install compass --norc && \
    ssh-keygen -A

RUN apk add --no-cache gawk

#install oh-my-bash
RUN wget https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh && \
    chmod u+x install.sh && \
    ./install.sh --prefix=/usr && \
    echo ". /etc/profile.d/bashrc.sh" >> /etc/bash/bashrc

RUN git clone --recursive --depth 1 --shallow-submodules https://github.com/akinomyoga/ble.sh.git && \
    make -C ble.sh install PREFIX=/usr

RUN curl -1sLf 'https://dl.cloudsmith.io/public/symfony/stable/setup.alpine.sh' | sudo -E bash
RUN apk add symfony-cli

#misc install and config
# USER root
# WORKDIR /root
RUN sed -i "s/;process_control_timeout = 0/process_control_timeout = 10s/g" /etc/php83/php-fpm.conf && \
    sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/g" /etc/ssh/sshd_config && \
    sed -i "s/#StrictModes yes/StrictModes no/g" /etc/ssh/sshd_config && \
    rm /etc/php83/php-fpm.d/www.conf && \
    mkdir -p /webcrate && \
    mkdir -p /webcrate-bin && \
    ln -s /bin/php83 /webcrate-bin/php && \
    chmod o-rwx /webcrate
    ###     sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php83/php.ini && \
    ###     echo 'dev ALL=(ALL) NOPASSWD: /bin/crontab' | EDITOR='tee -a' visudo && \
    ###     sed -i 's/test -r /test -e /g' /etc/profile && \
    ###     echo ". /etc/bash/bashrc" >> /etc/bash.bashrc

WORKDIR /
COPY ["bashrc.sh", "/etc/profile.d/"]
COPY ["versions.py", "parse-projects.py", "sync_ssh_keys.sh", "log.py", "supervisord.conf.template" "supervisord-user.conf.template", "/webcrate/"]
COPY ["entrypoint.sh", "/"]
RUN chmod u+x /webcrate/sync_ssh_keys.sh && \
    chmod u+x /webcrate/parse-projects.py && \
    chmod u+x /webcrate/versions.py && \
    chmod u+s /bin/ping && \
    chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
