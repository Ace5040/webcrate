ARG IMAGE_ALPINE_319_BASE
FROM $IMAGE_ALPINE_319_BASE

RUN apk update && apk add --no-cache sudo git nano exim openssh unzip mariadb-client mc iputils cronie wget tmux py3-pip python3 py3-yaml py3-munch libmemcached supervisor shadow

RUN chsh -s /bin/bash root

RUN adduser -D -s /bin/bash dev && \
    echo 'dev:dev' | chpasswd && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

USER root
WORKDIR /root

#install php81
RUN apk add --no-cache php81 php81-fileinfo php81-ctype php81-pear php81-zip php81-xmlreader php81-xmlwriter php81-mbstring php81-openssl php81-xml php81-fpm php81-intl php81-gd php81-xsl php81-simplexml php81-phar php81-tidy php81-tokenizer php81-curl php81-opcache php81-iconv php81-pdo php81-soap
RUN apk add --no-cache php81-pdo_sqlite php81-sqlite3 php81-pdo_mysql php81-mysqli php81-pecl-imagick
RUN apk add --no-cache php81-pecl-timezonedb php81-pecl-memcached
RUN apk add --no-cache composer ruby py3-setuptools py3-munch py3-pypdf bash make curl

#install ioncube
RUN wget https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz && \
    tar xzf ioncube_loaders_lin_x86-64.tar.gz && \
    cp ./ioncube/ioncube_loader_lin_8.1.so /usr/lib/php81/modules/ioncube_loader_lin.so && \
    rm -rf /root/ioncube && \
    rm -f /root/ioncube_loaders_lin_x86-64.tar.gz

RUN wget -O drush.phar https://github.com/drush-ops/drush-launcher/releases/latest/download/drush.phar && \
    chmod +x drush.phar && \
    mv drush.phar /usr/bin/drush && \
    ssh-keygen -A

RUN gem install rubygems-update && \
    gem update --system && \
    gem install compass

RUN apk add --no-cache gawk

#install oh-my-bash
RUN wget https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh && \
    chmod u+x install.sh && \
    ./install.sh --prefix=/usr

RUN git clone --recursive --depth 1 --shallow-submodules https://github.com/akinomyoga/ble.sh.git && \
    make -C ble.sh install PREFIX=/usr

RUN curl -1sLf 'https://dl.cloudsmith.io/public/symfony/stable/setup.alpine.sh' | sudo -E bash
RUN apk add symfony-cli

#misc config
RUN sed -i "s/;process_control_timeout = 0/process_control_timeout = 10s/g" /etc/php81/php-fpm.conf && \
    sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/g" /etc/ssh/sshd_config && \
    sed -i "s/#PasswordAuthentication yes/PasswordAuthentication yes/g" /etc/ssh/sshd_config && \
    sed -i "s/#StrictModes yes/StrictModes no/g" /etc/ssh/sshd_config && \
    echo ". /etc/bashrc.sh" >> /etc/profile && \
    cat > /etc/motd && \
    rm /etc/php81/php-fpm.d/www.conf && \
    mkdir -p /webcrate && \
    chmod o-rwx /webcrate

WORKDIR /
COPY ["versions.py", "parse-projects.py", "sync_ssh_keys.sh", "log.py", "supervisord.conf.template", "supervisord-user.conf.template", "/webcrate/"]
COPY bashrc.sh /etc/30-bashrc.sh
COPY ["entrypoint.sh", "/"]
RUN chmod u+x /webcrate/sync_ssh_keys.sh && \
    chmod u+x /webcrate/parse-projects.py && \
    chmod u+x /webcrate/versions.py && \
    chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
