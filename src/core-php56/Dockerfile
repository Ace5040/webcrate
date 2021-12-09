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

#install php 56
RUN sudo mkdir -p /opt/icu69; \
    wget "https://github.com/unicode-org/icu/releases/download/release-69-1/icu4c-69_1-src.tgz"; \
    tar zxvf ./icu4c-69_1-src.tgz; \
    cd ./icu/source; \
    ./configure --prefix="/opt/icu69" && make && sudo make install

RUN gpg --keyserver hkp://keyserver.ubuntu.com --recv-keys C2BF0BC433CFC8B3 FE857D9A90D90EC1; \
    git clone https://aur.archlinux.org/php56.git; \
    cd ./php56; \
    sed -i "s/--with-icu-dir=\/usr/--with-icu-dir=\/opt\/icu69/g" PKGBUILD; \
    makepkg -scir --nocheck --noconfirm; \
    rm -rf /home/dev/php56

#install php56-xdebug
RUN git clone https://aur.archlinux.org/php56-xdebug.git; \
    cd ./php56-xdebug; \
    sed -i '31,38d;51d' PKGBUILD; \
    makepkg -scir --noconfirm; \
    rm -rf /home/dev/php56-xdebug

#install php56-imagick php56-memcached
RUN yay --gpgflags "--keyserver hkp://keyserver.ubuntu.com" --noeditmenu --nodiffmenu --noconfirm --mflags --nocheck -S php56-imagick php56-memcached; \
    yes | yay -Scc; \
    rm -rf /home/dev/.cache

#misc install and config
USER root
WORKDIR /root
RUN wget -O drush.phar https://github.com/drush-ops/drush-launcher/releases/download/0.8.0/drush.phar; \
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
    systemctl enable php56-fpm; \
    systemctl enable sshd; \
    systemctl enable cronie; \
    systemctl enable telegraf; \
    systemctl enable exim; \
    printf "\ninclude=/etc/php56/php-fpm.d/*.conf" >> /etc/php56/php-fpm.conf; \
    sed -i "s/;process_control_timeout = 0/process_control_timeout = 10s/g"  /etc/php56/php-fpm.conf; \
    sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php56/php.ini; \
    sed -i "s/# urls = \[\"http\:\/\/127\.0\.0\.1\:8086\"\]/urls = \[\"http\:\/\/webcrate-influxdb\:8086\"\]/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/# skip_database_creation = false/skip_database_creation = true/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/# database = \"telegraf\"/database = \"telegraf\"/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/g" /etc/ssh/sshd_config; \
    sed -i "s/#StrictModes yes/StrictModes no/g" /etc/ssh/sshd_config; \
    rm /etc/php56/conf.d/imagick.ini; \
    rm /etc/php56/conf.d/xdebug.ini; \
    echo ". /etc/profile.d/bashrc.sh" >> /etc/bash.bashrc; \
    echo 'dev ALL=(ALL) NOPASSWD: /bin/crontab' | EDITOR='tee -a' visudo; \
    sed -i 's/test -r /test -e /g' /etc/profile; \
    mkdir -p /webcrate; \
    mkdir -p /webcrate-bin; \
    mkdir -p /webcrate-bin/php56; \
    ln -s /bin/php56 /webcrate-bin/php56/php; \
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
    cp ./ioncube/ioncube_loader_lin_5.6.so /usr/lib/php56/modules/ioncube_loader_lin.so; \
    rm -rf /root/ioncube; \
    rm -f /root/ioncube_loaders_lin_x86-64.tar.gz; \
    ln -s /opt/icu69/lib/libicui18n.so.69.1 /usr/lib/libicui18n.so.69; \
    ln -s /opt/icu69/lib/libicuuc.so.69.1 /usr/lib/libicuuc.so.69; \
    ln -s /opt/icu69/lib/libicudata.so.69.1 /usr/lib/libicudata.so.69; \
    ln -s /opt/icu69/lib/libicuio.so.69.1 /usr/lib/libicuio.so.69

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
