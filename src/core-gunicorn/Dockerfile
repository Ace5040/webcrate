ARG IMAGE=debian:trixie-slim
FROM $IMAGE

RUN sed -i "s/deb.debian.org/mirror.truenetwork.ru/g" /etc/apt/sources.list.d/debian.sources
RUN apt-get update
RUN apt-get --assume-yes install sudo git nano exim4-base openssh-server \
    unzip mariadb-client postgresql-client mc iputils-ping cron wget tmux supervisor \
    curl lsb-release ca-certificates ruby ruby-dev \
    python3 python3-pip python3-yaml python3-munch libmemcached-tools python3-pypdf


    RUN usermod -s /bin/bash root

    RUN adduser --no-create-home --disabled-login -shell /bin/bash dev && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

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

    #misc config
    RUN sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/g" /etc/ssh/sshd_config && \
    sed -i "s/#PasswordAuthentication yes/PasswordAuthentication yes/g" /etc/ssh/sshd_config && \
    sed -i "s/#StrictModes yes/StrictModes no/g" /etc/ssh/sshd_config && \
    sed -i "s/PrintMotd no/PrintMotd yes/g" /etc/ssh/sshd_config && \
    cat > /etc/motd && \
    ln -s /usr/lib/x86_64-linux-gnu/libcrypt.so.1 /usr/lib/x86_64-linux-gnu/libcrypt.so.2 && \
    cp /usr/share/zoneinfo/Europe/Kyiv /usr/share/zoneinfo/Europe/Kiev && \
    rm /etc/update-motd.d/10-uname && \
    mkdir -p /webcrate && \
    chmod o-rwx /webcrate

RUN export PYENV_ROOT=/opt/pyenv; curl https://pyenv.run | bash

WORKDIR /
COPY ["versions.py", "parse-projects.py", "sync_ssh_keys.sh", "log.py", "supervisord.conf.template", "supervisord-user.conf.template", "/webcrate/"]
COPY bashrc.sh /etc/bashrc.sh
COPY ["gunicorn_restart.sh", "/webcrate-bin/"]
COPY ["entrypoint.sh", "/"]
RUN chmod a+x /webcrate-bin/gunicorn_restart.sh && \
    chmod u+x /webcrate/sync_ssh_keys.sh && \
    chmod u+x /webcrate/parse-projects.py && \
    chmod u+x /webcrate/versions.py && \
    chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
EXPOSE 22 9000
WORKDIR /
