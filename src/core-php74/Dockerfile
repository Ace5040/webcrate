FROM archlinux:latest

#set mirror
RUN echo "Server = https://mirror.yandex.ru/archlinux/\$repo/os/\$arch" >> /etc/pacman.d/mirrorlist

#php repo
RUN sed -Ei "s/default mirrors./default mirrors.\n\n[home_el_archphp_Arch]\nServer = https:\/\/download.opensuse.org\/repositories\/home:\/el:\/archphp\/Arch\/\$arch/g" /etc/pacman.conf && \
    key=$(curl -fsSL https://download.opensuse.org/repositories/home:el:archphp/Arch/$(uname -m)/home_el_archphp_Arch.key) && \
    fingerprint=$(gpg --quiet --with-colons --import-options show-only --import --fingerprint <<< "${key}" | awk -F: '$1 == "fpr" { print $10 }') && \
    pacman-key --init && \
    pacman-key --add - <<< "${key}" && \
    pacman-key --lsign-key "${fingerprint}"

#install system utils and services
RUN pacman --needed --noconfirm -Syu && \
    pacman --needed --noconfirm -S sudo git nano exim openssh base-devel unzip npm mariadb-clients mc iputils cronie inetutils wget tmux ruby python-pip libmemcached-awesome && \
    yes | pacman -Scc && \
    useradd -m -s /bin/bash dev && \
    usermod -p "dev" dev && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo && \
    sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j12\"/g" /etc/makepkg.conf

#install php74
RUN pacman --needed --noconfirm -S php74 php74-fileinfo php74-ctype php74-json php74-pecl php74-pear php74-zip php74-xmlreader php74-xmlwriter php74-mbstring php74-openssl php74-xml php74-fpm php74-intl php74-sqlite php74-gd php74-xsl php74-simplexml php74-phar php74-tidy php74-cli php74-tokenizer php74-curl php74-opcache php74-iconv php74-mysql php74-pdo php74-soap php74-imagick
RUN pecl74 install timezonedb-2021.5 memcached && \
    echo extension=timezonedb.so > /etc/php74/conf.d/10-timezonedb.ini && \
    echo extension=memcached.so > /etc/php74/conf.d/10-memcached.ini

USER dev
WORKDIR /home/dev

#install oh-my-bash
RUN git clone https://aur.archlinux.org/oh-my-bash-git.git && \
    cd oh-my-bash-git && \
    makepkg -scir --nocheck --noconfirm --skipchecksums && \
    rm -rf /home/dev/oh-my-bash-git

#install blesh-git
RUN git clone https://aur.archlinux.org/blesh-git.git && \
    cd blesh-git && \
    makepkg -scir --nocheck --noconfirm --skipchecksums && \
    rm -rf /home/dev/blesh-git

#install symfony-cli-bin
RUN git clone https://aur.archlinux.org/symfony-cli-bin.git && \
    cd symfony-cli-bin && \
    makepkg -scir --nocheck --noconfirm --skipchecksums && \
    rm -rf /home/dev/symfony-cli-bin

#install docker-systemctl-replacement-git
RUN git clone https://aur.archlinux.org/docker-systemctl-replacement-git.git && \
    cd docker-systemctl-replacement-git && \
    makepkg -scir --nocheck --noconfirm --skipchecksums && \
    rm -rf /home/dev/docker-systemctl-replacement-git

#misc
USER root
WORKDIR /root

RUN wget -O drush.phar https://github.com/drush-ops/drush-launcher/releases/latest/download/drush.phar && \
    chmod +x drush.phar && \
    mv drush.phar /usr/bin/drush && \
    wget -O composer.phar https://getcomposer.org/download/latest-stable/composer.phar && \
    chmod +x composer.phar && \
    mv composer.phar /usr/bin/composer && \
    gem install compass --norc && \
    pip install --break-system-packages pyyml munch setuptools && \
    chown root:root /bin/systemctl.py && \
    chmod a+x /bin/systemctl.py && \
    mv /bin/systemctl /bin/systemctl_original && \
    cp /bin/systemctl.py /bin/systemctl && \
    ssh-keygen -A && \
    systemctl enable php74-fpm && \
    systemctl enable sshd && \
    systemctl enable cronie && \
    systemctl enable exim && \
    sed -i "s/;process_control_timeout = 0/process_control_timeout = 10s/g"  /etc/php74/php-fpm.conf && \
    sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php74/php.ini && \
    sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/g" /etc/ssh/sshd_config && \
    sed -i "s/#StrictModes yes/StrictModes no/g" /etc/ssh/sshd_config && \
    echo ". /etc/profile.d/bashrc.sh" >> /etc/bash.bashrc && \
    echo 'dev ALL=(ALL) NOPASSWD: /bin/crontab' | EDITOR='tee -a' visudo && \
    sed -i 's/test -r /test -e /g' /etc/profile && \
    mkdir -p /webcrate && \
    mkdir -p /webcrate-bin && \
    ln -s /bin/php74 /webcrate-bin/php && \
    chmod o-rwx /webcrate

#install ioncucbe
RUN wget https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz && \
    tar xzf ioncube_loaders_lin_x86-64.tar.gz && \
    cp ./ioncube/ioncube_loader_lin_7.4.so /usr/lib/php74/modules/ioncube_loader_lin.so && \
    rm -rf /root/ioncube && \
    rm -f /root/ioncube_loaders_lin_x86-64.tar.gz

WORKDIR /
#copy scripts
COPY ["bashrc.sh", "/etc/profile.d/"]
COPY ["versions.py", "parse-projects.py", "sync_ssh_keys.sh", "log.py", "/webcrate/"]
COPY ["entrypoint.sh", "/"]
RUN chmod u+x /webcrate/sync_ssh_keys.sh && \
    rm /etc/mail/exim.conf && \
    chmod u+x /webcrate/parse-projects.py && \
    chmod u+x /webcrate/versions.py && \
    chmod u+s /bin/ping && \
    chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
