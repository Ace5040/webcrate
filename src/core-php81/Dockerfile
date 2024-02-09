FROM archlinux:latest

#install system utils and services
RUN pacman --needed --noconfirm -Syu && \
    pacman --needed --noconfirm -S sudo git nano exim openssh base-devel unzip npm mariadb-clients mc iputils cronie inetutils wget tmux ruby python-pip fish libmemcached-awesome libreoffice ttf-liberation fuse2 fuse3 && \
    yes | pacman -Scc && \
    useradd -m -s /bin/bash dev && \
    usermod -p "dev" dev && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo && \
    sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j12\"/g" /etc/makepkg.conf

#install yay
WORKDIR /home/dev/yay
RUN chown dev:dev /home/dev/yay
USER dev
RUN git clone https://aur.archlinux.org/yay.git .; \
    makepkg -scir --noconfirm; \
    rm -rf /home/dev/yay

WORKDIR /home/dev
USER dev

#install aur packages
RUN yay --gpgflags "--keyserver hkp://keyserver.ubuntu.com" --noeditmenu --nodiffmenu --noconfirm --mflags --nocheck -S php81 php81-exif php81-fileinfo php81-ctype php81-pecl php81-pear php81-zip php81-xmlreader php81-xmlwriter php81-mbstring php81-openssl php81-xml php81-fpm php81-intl php81-sqlite php81-gd php81-xsl php81-simplexml php81-phar php81-tidy php81-cli php81-tokenizer php81-curl php81-opcache php81-iconv php81-mysql php81-pdo php81-soap php81-imagick && \
    yes | yay -Scc && \
    rm -rf /home/dev/.cache

USER root
RUN pecl81 install timezonedb-2021.5 memcached && \
    echo extension=timezonedb.so > /etc/php81/conf.d/10-timezonedb.ini && \
    echo extension=memcached.so > /etc/php81/conf.d/10-memcached.ini

USER dev
#install symfony-cli-bin
RUN git clone https://aur.archlinux.org/symfony-cli-bin.git && \
    cd symfony-cli-bin && \
    makepkg -scir --nocheck --noconfirm --skipchecksums && \
    rm -rf /home/dev/symfony-cli-bin

#install pdf2htmlex-appimage
RUN git clone https://aur.archlinux.org/pdf2htmlex-appimage.git && \
    cd pdf2htmlex-appimage && \
    makepkg -scir --nocheck --noconfirm --skipchecksums && \
    rm -rf /home/dev/pdf2htmlex-appimage

#install docker-systemctl-replacement-git
RUN git clone https://aur.archlinux.org/docker-systemctl-replacement-git.git && \
    cd docker-systemctl-replacement-git && \
    makepkg -scir --nocheck --noconfirm --skipchecksums && \
    rm -rf /home/dev/docker-systemctl-replacement-git

#misc install and config
USER root
WORKDIR /root
RUN wget -O drush.phar https://github.com/drush-ops/drush-launcher/releases/latest/download/drush.phar && \
    chmod +x drush.phar && \
    mv drush.phar /usr/bin/drush && \
    wget -O composer.phar https://getcomposer.org/download/latest-stable/composer.phar && \
    chmod +x composer.phar && \
    mv composer.phar /usr/bin/composer && \
    gem install compass --norc && \
    pip install --break-system-packages pyyml munch setuptools PyPDF2 python-docx && \
    chown root:root /bin/systemctl.py && \
    chmod a+x /bin/systemctl.py && \
    mv /bin/systemctl /bin/systemctl_original && \
    cp /bin/systemctl.py /bin/systemctl && \
    ssh-keygen -A && \
    systemctl enable php81-fpm && \
    systemctl enable sshd && \
    systemctl enable cronie && \
    systemctl enable exim && \
    sed -i "s/;process_control_timeout = 0/process_control_timeout = 10s/g"  /etc/php81/php-fpm.conf && \
    sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php81/php.ini && \
    sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/g" /etc/ssh/sshd_config && \
    sed -i "s/#StrictModes yes/StrictModes no/g" /etc/ssh/sshd_config && \
    echo ". /etc/profile.d/bashrc.sh" >> /etc/bash.bashrc && \
    echo 'dev ALL=(ALL) NOPASSWD: /bin/crontab' | EDITOR='tee -a' visudo && \
    sed -i 's/test -r /test -e /g' /etc/profile && \
    mkdir -p /webcrate && \
    mkdir -p /webcrate-bin && \
    ln -s /bin/php81 /webcrate-bin/php && \
    mkdir -p /webcrate-fish && \
    chmod o-rwx /webcrate

#install fish
WORKDIR /webcrate-fish/oh-my-fish
RUN git clone https://github.com/oh-my-fish/oh-my-fish . && \
    bin/install --offline --path=/webcrate-fish/omf --noninteractive --config=/webcrate-fish/omfconf && \
    rm -rf ./* && \
    cp /root/.config/fish/conf.d/omf.fish /etc/fish/conf.d/omf.fish && \
    fish -C "omf install cbjohnson" && \
    cp /webcrate-fish/omf/themes/default/functions/fish_right_prompt.fish /webcrate-fish/omf/themes/cbjohnson/fish_right_prompt.fish;
COPY fish_prompt.fish /webcrate-fish/omf/themes/cbjohnson/fish_prompt.fish

#install ioncucbe
RUN wget https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz && \
    tar xzf ioncube_loaders_lin_x86-64.tar.gz && \
    cp ./ioncube/ioncube_loader_lin_8.1.so /usr/lib/php81/modules/ioncube_loader_lin.so && \
    rm -rf /root/ioncube && \
    rm -f /root/ioncube_loaders_lin_x86-64.tar.gz

WORKDIR /
COPY ["fishrc.fish", "/etc/fish/conf.d/"]
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
