ARG IMAGE=debian:trixie-slim
FROM $IMAGE

RUN sed -i "s/deb.debian.org/mirror.truenetwork.ru/g" /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get --assume-yes --no-install-recommends install \
        sudo git exim4-base openssh-server \
        unzip mariadb-client postgresql-client iputils-ping cron wget tmux supervisor \
        curl lsb-release ca-certificates ruby ruby-dev make gawk \
        python3 python3-pip python3-yaml python3-munch libmemcached-tools python3-pypdf && \
    rm -rf /var/lib/apt/lists/*

RUN usermod -s /bin/bash root && \
    adduser --no-create-home --disabled-login -shell /bin/bash dev && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

# Install compass + oh-my-bash + ble.sh, then purge build deps
RUN apt-get update && \
    apt-get --assume-yes --no-install-recommends install gcc libffi-dev && \
    gem install compass --no-document && \
    gem cleanup && \
    wget -q https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh && \
    chmod u+x install.sh && \
    ./install.sh --prefix=/usr && \
    rm install.sh && \
    git clone --recursive --depth 1 --shallow-submodules https://github.com/akinomyoga/ble.sh.git && \
    make -C ble.sh install PREFIX=/usr && \
    rm -rf ble.sh && \
    apt-get --assume-yes purge gcc libffi-dev && \
    apt-get --assume-yes autoremove && \
    rm -rf /var/lib/apt/lists/*

# Install pyenv
RUN export PYENV_ROOT=/opt/pyenv && curl https://pyenv.run | bash

# Misc config
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

WORKDIR /
COPY ["versions.py", "parse-projects.py", "sync_ssh_keys.sh", "supervisord.conf.template", "supervisord-user.conf.template", "/webcrate/"]
COPY --from=src log.py /webcrate/
COPY bashrc.sh /etc/bashrc.sh
COPY ["gunicorn_restart.sh", "/webcrate-bin/"]
COPY ["entrypoint.sh", "/"]
RUN chmod a+x /webcrate-bin/gunicorn_restart.sh && \
    chmod u+x \
        /webcrate/sync_ssh_keys.sh \
        /webcrate/parse-projects.py \
        /webcrate/versions.py \
        /entrypoint.sh
CMD ["/entrypoint.sh"]
EXPOSE 22 9000
