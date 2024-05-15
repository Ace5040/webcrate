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
    pacman --needed --noconfirm -S sudo git nano exim openssh base-devel unzip npm mc iputils cronie inetutils wget tmux ruby python-pip fish libmemcached-awesome && \
    yes | pacman -Scc && \
    useradd -m -s /bin/bash dev && \
    usermod -p "dev" dev && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo && \
    sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j12\"/g" /etc/makepkg.conf

#install php56
RUN pacman --needed --noconfirm -S php56 php56-fileinfo php56-ctype php56-json php56-pecl php56-pear php56-zip php56-xmlreader php56-xmlwriter php56-mbstring php56-xml php56-fpm php56-intl php56-sqlite php56-gd php56-xsl php56-simplexml php56-phar php56-tidy php56-cli php56-tokenizer php56-curl php56-opcache php56-iconv php56-mysql php56-pdo php56-soap php56-imagick
RUN pecl56 install timezonedb-2021.5 && \
    echo extension=timezonedb.so > /etc/php56/conf.d/10-timezonedb.ini

# #install mysql5 compatible mariadb-clients
RUN pacman --needed --noconfirm -U https://archive.archlinux.org/packages/m/mariadb-libs/mariadb-libs-10.10.3-1-x86_64.pkg.tar.zst https://archive.archlinux.org/packages/m/mariadb-clients/mariadb-clients-10.10.3-1-x86_64.pkg.tar.zst

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

#misc install and config
USER root

WORKDIR /root
RUN wget -O drush.phar https://github.com/drush-ops/drush-launcher/releases/download/0.8.0/drush.phar && \
    chmod +x drush.phar && \
    mv drush.phar /usr/bin/drush && \
    wget -O composer.phar https://getcomposer.org/download/latest-2.2.x/composer.phar && \
    chmod +x composer.phar && \
    mv composer.phar /usr/bin/composer && \
    gem install compass --norc && \
    pip install --break-system-packages pyyml munch setuptools && \
    chown root:root /bin/systemctl.py && \
    chmod a+x /bin/systemctl.py && \
    mv /bin/systemctl /bin/systemctl_original && \
    cp /bin/systemctl.py /bin/systemctl && \
    ssh-keygen -A && \
    systemctl enable php56-fpm && \
    systemctl enable sshd && \
    systemctl enable cronie && \
    systemctl enable exim && \
    printf "\ninclude=/etc/php56/php-fpm.d/*.conf" >> /etc/php56/php-fpm.conf && \
    sed -i "s/;process_control_timeout = 0/process_control_timeout = 10s/g"  /etc/php56/php-fpm.conf && \
    sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php56/php.ini && \
    sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/g" /etc/ssh/sshd_config && \
    sed -i "s/#StrictModes yes/StrictModes no/g" /etc/ssh/sshd_config && \
    echo ". /etc/profile.d/bashrc.sh" >> /etc/bash.bashrc && \
    echo 'dev ALL=(ALL) NOPASSWD: /bin/crontab' | EDITOR='tee -a' visudo && \
    sed -i 's/test -r /test -e /g' /etc/profile && \
    mkdir -p /webcrate && \
    mkdir -p /webcrate-bin && \
    ln -s /bin/php56 /webcrate-bin/php && \
    chmod o-rwx /webcrate

#install ioncucbe
RUN wget https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz && \
    tar xzf ioncube_loaders_lin_x86-64.tar.gz && \
    cp ./ioncube/ioncube_loader_lin_5.6.so /usr/lib/php56/modules/ioncube_loader_lin.so && \
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
