FROM archlinux:latest
RUN echo "Set disable_coredump false" >> /etc/sudo.conf
RUN pacman --noconfirm -Syu
RUN pacman --needed --noconfirm -S git nano openssh base-devel unzip composer npm mariadb-clients dnsmasq mc iputils cronie inetutils which ruby python-pip python-virtualenv wget
RUN pacman --needed --noconfirm -S php php-fpm php-intl php-sqlite php-gd php-xsl php-intl php-tidy php-imagick php-memcached xdebug
RUN useradd -m -s /bin/bash dev
RUN usermod -p "dev" dev
RUN echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo
RUN sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j6\"/g" /etc/makepkg.conf
USER dev
WORKDIR /home/dev
RUN git clone https://aur.archlinux.org/yay.git
WORKDIR /home/dev/yay
RUN makepkg -scir --noconfirm
WORKDIR /home/dev
RUN gpg --keyserver keys.gnupg.net --recv-key CBAF69F173A0FEA4B537F470D66C9593118BCCB6 F38252826ACD957EF380D39F2F7956BC5DA04B5D C2BF0BC433CFC8B3
RUN yay --noeditmenu --nodiffmenu --noconfirm -S --mflags --nocheck php73 php73-fpm php73-intl php73-sqlite php73-gd php73-xsl php73-intl php73-tidy php73-imagick php73-memcached php73-xdebug
RUN yay --noeditmenu --nodiffmenu --noconfirm -S --mflags --nocheck php56 php56-fpm php56-intl php56-sqlite php56-gd php56-xsl php56-intl php56-tidy php56-imagick php56-memcached
RUN gpg --keyserver keys.gnupg.net --recv-key 32E4B74757B1D65234FC389F293D771241515FE8
RUN yay --noeditmenu --nodiffmenu --noconfirm -S docker-systemctl-replacement-git drush-launcher symfony-cli telegraf-bin tmux fish proftpd
USER root
RUN gem install compass --norc
RUN pip install pyyml munch
RUN pacman --noconfirm -R postfix
RUN pacman --noconfirm -S exim
RUN chown root:root /bin/systemctl.py
RUN chmod a+x /bin/systemctl.py
RUN mv /bin/systemctl /bin/systemctl_original
RUN cp /bin/systemctl.py /bin/systemctl
RUN ssh-keygen -A
RUN systemctl enable php-fpm; \
    systemctl enable php73-fpm; \
    systemctl enable php56-fpm; \
    systemctl enable sshd; \
    systemctl enable cronie; \
    systemctl enable telegraf; \
    systemctl enable exim; \
    systemctl enable dnsmasq; \
    systemctl enable proftpd
RUN printf "\ninclude=/etc/php56/php-fpm.d/*.conf" >> /etc/php56/php-fpm.conf; \
    sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php/php.ini; \
    sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php73/php.ini; \
    sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php56/php.ini; \
    sed -i "s/;extension=imagick/extension=imagick/g" /etc/php/conf.d/imagick.ini; \
    sed -i "s/;extension=imagick/extension=imagick/g" /etc/php73/conf.d/imagick.ini; \
    sed -i "s/# urls = \[\"http\:\/\/127\.0\.0\.1\:8086\"\]/urls = \[\"http\:\/\/influxdb\:8086\"\]/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/# skip_database_creation = false/skip_database_creation = true/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/# database = \"telegraf\"/database = \"telegraf\"/g" /etc/telegraf/telegraf.conf;
#    sed -i 's/  interval = "10s"/  interval = "1s"/g' /etc/telegraf/telegraf.conf
WORKDIR /
COPY proftpd.conf /etc/proftpd.conf
RUN printf "no-resolv\nno-poll\nno-hosts\naddn-hosts=/webcrate/dnsmasq_hosts/hosts_nginx\n" > /etc/dnsmasq.conf
RUN echo ". /etc/profile.d/bashrc.sh" >> /etc/bash.bashrc
RUN mkdir -p /webcrate; \
    mkdir -p /webcrate/bin; \
    mkdir -p /webcrate/bin/php; \
    mkdir -p /webcrate/bin/php73; \
    mkdir -p /webcrate/bin/php56; \
    ln -s /bin/php /webcrate/bin/php/php; \
    ln -s /bin/php73 /webcrate/bin/php73/php; \
    ln -s /bin/php56 /webcrate/bin/php56/php; \
    mkdir -p /webcrate/fish
WORKDIR /webcrate/fish
RUN git clone https://github.com/oh-my-fish/oh-my-fish
WORKDIR /webcrate/fish/oh-my-fish
RUN bin/install --offline --path=/webcrate/fish/omf --config=/webcrate/fish/omfconf; \
    cp /root/.config/fish/conf.d/omf.fish /etc/fish/conf.d/omf.fish; \
    fish -C "omf install cbjohnson"; \
    cp /webcrate/fish/omf/themes/default/fish_right_prompt.fish /webcrate/fish/omf/themes/cbjohnson/fish_right_prompt.fish
COPY fish_prompt.fish /webcrate/fish/omf/themes/cbjohnson/fish_prompt.fish
WORKDIR /root
RUN wget https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz; \
    tar xzvf ioncube_loaders_lin_x86-64.tar.gz; \
    cp ioncube/ioncube_loader_lin_7.4.so /usr/lib/php/modules/ioncube_loader_lin.so; \
    cp ioncube/ioncube_loader_lin_7.3.so /usr/lib/php73/modules/ioncube_loader_lin.so; \
    cp ioncube/ioncube_loader_lin_5.6.so /usr/lib/php56/modules/ioncube_loader_lin.so; \
    rm /etc/php73/conf.d/xdebug.ini; \
    yes | sudo symfony self-update
WORKDIR /
COPY sync_ssh_keys.sh /webcrate/sync_ssh_keys.sh
COPY stats_users.sh /webcrate/stats_users.sh
COPY stats_pools.sh /webcrate/stats_pools.sh
COPY bashrc.sh /etc/profile.d/bashrc.sh
COPY fishrc.fish /etc/fish/conf.d/fishrc.fish
COPY toprc /etc/telegraf/.config/procps/toprc
COPY gunicorn_restart.sh /webcrate/bin/gunicorn_restart.sh
COPY parse-users.py /webcrate/parse-users.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod u+x /webcrate/sync_ssh_keys.sh; \
    chmod a+x /webcrate/stats_users.sh; \
    chmod a+x /webcrate/stats_pools.sh; \
    mkdir -p /etc/telegraf/.config/procps; \
    rm /etc/mail/exim.conf; \
    chmod a+x /webcrate/bin/gunicorn_restart.sh; \
    chmod a+x /webcrate/parse-users.py; \
    chmod u+x /entrypoint.sh
WORKDIR /webcrate
CMD ["/entrypoint.sh"]
