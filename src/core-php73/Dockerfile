FROM archlinux:latest

#install system utils and services
RUN pacman --needed --noconfirm -Syu; \
    pacman --needed --noconfirm -S git nano openssh base-devel unzip composer npm mariadb-clients mc iputils cronie inetutils wget tmux ruby python-pip fish; \
    yes | pacman -Scc; \
    useradd -m -s /bin/bash dev; \
    usermod -p "dev" dev; \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo; \
    sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j6\"/g" /etc/makepkg.conf
WORKDIR /home/dev

#install yay
USER dev
RUN git clone https://aur.archlinux.org/yay.git; \
    cd ./yay; makepkg -scir --noconfirm; \
    rm -rf /home/dev/yay

#install aur packages
RUN yay --gpgflags "--keyserver hkp://keyserver.ubuntu.com" --noeditmenu --nodiffmenu --noconfirm --mflags --nocheck -S docker-systemctl-replacement-git symfony-cli telegraf-bin; \
    yes | yay -Scc; \
    rm -rf /home/dev/.cache

#install php 73
RUN gpg --keyserver hkp://keyserver.ubuntu.com --recv-keys 2F7956BC5DA04B5D D66C9593118BCCB6; \
    git clone https://aur.archlinux.org/php73.git; \
    cd ./php73; \
    wget https://gitweb.gentoo.org/repo/gentoo.git/plain/dev-lang/php/files/php-icu-70.patch; \
    sed -i "s/'freetype.patch'/'freetype.patch' 'php-icu-70.patch'/g" PKGBUILD; \
    sed -i "s/patch -p1 -i \${srcdir}\/freetype.patch/patch -p1 -i \${srcdir}\/freetype.patch; patch -p1 -i \${srcdir}\/php-icu-70.patch/g" PKGBUILD; \
    makepkg -scir --nocheck --noconfirm --skipchecksums; \
    rm -rf /home/dev/php73

#install php73-imagick php73-memcached php73-xdebug
RUN yay --gpgflags "--keyserver hkp://keyserver.ubuntu.com" --noeditmenu --nodiffmenu --noconfirm --mflags --nocheck -S php73-imagick php73-memcached php73-xdebug; \
    yes | yay -Scc; \
    rm -rf /home/dev/.cache

#misc install and config
USER root
WORKDIR /root
RUN wget -O drush.phar https://github.com/drush-ops/drush-launcher/releases/latest/download/drush.phar; \
    chmod +x drush.phar; \
    mv drush.phar /usr/bin/drush; \
    gem install compass --norc; \
    pip install pyyml munch; \
    pacman --needed --noconfirm -S exim; \
    yes | pacman -Scc; \
    chown root:root /bin/systemctl.py; \
    chmod a+x /bin/systemctl.py; \
    mv /bin/systemctl /bin/systemctl_original; \
    cp /bin/systemctl.py /bin/systemctl; \
    ssh-keygen -A; \
    systemctl enable php73-fpm; \
    systemctl enable sshd; \
    systemctl enable cronie; \
    systemctl enable telegraf; \
    systemctl enable exim; \
    sed -i "s/;process_control_timeout = 0/process_control_timeout = 10s/g"  /etc/php73/php-fpm.conf; \
    sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php73/php.ini; \
    sed -i "s/# urls = \[\"http\:\/\/127\.0\.0\.1\:8086\"\]/urls = \[\"http\:\/\/webcrate-influxdb\:8086\"\]/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/# skip_database_creation = false/skip_database_creation = true/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/# database = \"telegraf\"/database = \"telegraf\"/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/g" /etc/ssh/sshd_config; \
    sed -i "s/#StrictModes yes/StrictModes no/g" /etc/ssh/sshd_config; \
    rm /etc/php73/conf.d/imagick.ini; \
    rm /etc/php73/conf.d/xdebug.ini; \
    echo ". /etc/profile.d/bashrc.sh" >> /etc/bash.bashrc; \
    echo 'dev ALL=(ALL) NOPASSWD: /bin/crontab' | EDITOR='tee -a' visudo; \
    sed -i 's/test -r /test -e /g' /etc/profile; \
    mkdir -p /webcrate; \
    mkdir -p /webcrate-bin; \
    mkdir -p /webcrate-bin/php73; \
    ln -s /bin/php73 /webcrate-bin/php73/php; \
    mkdir -p /webcrate-fish; \
    chmod o-rwx /webcrate; \
    mkdir -p /webcrate-telegraf; \
    yes | sudo symfony self-update; \
    chown telegraf:telegraf /webcrate-telegraf; \
    chmod o-rwx /webcrate-telegraf;

#install fish
WORKDIR /webcrate-fish/oh-my-fish
RUN git clone https://github.com/oh-my-fish/oh-my-fish .; \
    bin/install --offline --path=/webcrate-fish/omf --noninteractive --config=/webcrate-fish/omfconf; \
    rm -rf ./*; \
    cp /root/.config/fish/conf.d/omf.fish /etc/fish/conf.d/omf.fish; \
    fish -C "omf install cbjohnson"; \
    cp /webcrate-fish/omf/themes/default/functions/fish_right_prompt.fish /webcrate-fish/omf/themes/cbjohnson/fish_right_prompt.fish;
COPY fish_prompt.fish /webcrate-fish/omf/themes/cbjohnson/fish_prompt.fish

#install ioncucbe
RUN wget https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz; \
    tar xzf ioncube_loaders_lin_x86-64.tar.gz; \
    cp ./ioncube/ioncube_loader_lin_7.3.so /usr/lib/php73/modules/ioncube_loader_lin.so; \
    rm -rf /root/ioncube; \
    rm -f /root/ioncube_loaders_lin_x86-64.tar.gz

WORKDIR /
#copy scripts
COPY ["toprc", "/etc/telegraf/.config/procps/"]
COPY ["fishrc.fish", "/etc/fish/conf.d/"]
COPY ["bashrc.sh", "/etc/profile.d/"]
COPY ["stats_projects.sh", "stats_pools.sh", "/webcrate-telegraf/"]
COPY ["versions.py", "parse-projects.py", "sync_ssh_keys.sh", "log.py", "/webcrate/"]
COPY ["entrypoint.sh", "/"]
RUN chmod u+x /webcrate/sync_ssh_keys.sh; \
    chmod a+x /webcrate-telegraf/stats_projects.sh; \
    chmod a+x /webcrate-telegraf/stats_pools.sh; \
    mkdir -p /etc/telegraf/.config/procps; \
    rm /etc/mail/exim.conf; \
    chmod u+x /webcrate/parse-projects.py; \
    chmod u+x /webcrate/versions.py; \
    chmod u+s /bin/ping; \
    chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
