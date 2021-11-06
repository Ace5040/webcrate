FROM archlinux:latest

#update pacman db
RUN pacman --needed --noconfirm -Syu

#install system utils and services
RUN pacman --needed --noconfirm -S git nano openssh base-devel unzip composer npm mariadb-clients mc iputils cronie inetutils which wget tmux ruby python-pip fish

#install latest php
RUN pacman --needed --noconfirm -S php php-fpm php-intl php-sqlite php-gd php-xsl php-tidy php-imagick php-memcached xdebug

#add dev user
RUN useradd -m -s /bin/bash dev
RUN usermod -p "dev" dev

#grant dev user sudo priviledges
RUN echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

#enable 6 cores support for make
RUN sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j6\"/g" /etc/makepkg.conf
USER dev
WORKDIR /home/dev

#install yay
RUN git clone https://aur.archlinux.org/yay.git
WORKDIR /home/dev/yay
RUN makepkg -scir --noconfirm
WORKDIR /home/dev

#remove yay src
RUN rm -rf /home/dev/yay

#install soft from aur
RUN yay --gpgflags "--keyserver hkp://keyserver.ubuntu.com" --noeditmenu --nodiffmenu --noconfirm --mflags --nocheck -S docker-systemctl-replacement-git symfony-cli telegraf-bin vue-cli

USER root

#install drush
RUN wget -O drush.phar https://github.com/drush-ops/drush-launcher/releases/latest/download/drush.phar; \
    chmod +x drush.phar; \
    mv drush.phar /usr/bin/drush

#install legacy drush
RUN wget -O drush.0.8.0.phar https://github.com/drush-ops/drush-launcher/releases/download/0.8.0/drush.phar; \
    chmod +x drush.0.8.0.phar; \
    mv drush.0.8.0.phar /usr/bin/drush.0.8.0

#install compass
RUN gem install compass --norc

#install phyton libs
RUN pip install pyyml munch

#replace postfix with exim
# RUN pacman --noconfirm -R postfix
RUN pacman --needed --noconfirm -S exim

RUN chown root:root /bin/systemctl.py
RUN chmod a+x /bin/systemctl.py
RUN mv /bin/systemctl /bin/systemctl_original
RUN cp /bin/systemctl.py /bin/systemctl
RUN ssh-keygen -A
RUN systemctl enable php-fpm; \
    systemctl enable sshd; \
    systemctl enable cronie; \
    systemctl enable telegraf; \
    systemctl enable exim;

RUN sed -i "s/;process_control_timeout = 0/process_control_timeout = 10s/g"  /etc/php/php-fpm.conf; \
    sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php/php.ini; \
    sed -i "s/# urls = \[\"http\:\/\/127\.0\.0\.1\:8086\"\]/urls = \[\"http\:\/\/influxdb\:8086\"\]/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/# skip_database_creation = false/skip_database_creation = true/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/# database = \"telegraf\"/database = \"telegraf\"/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/g" /etc/ssh/sshd_config; \
    sed -i "s/#StrictModes yes/StrictModes no/g" /etc/ssh/sshd_config;
WORKDIR /

RUN echo ". /etc/profile.d/bashrc.sh" >> /etc/bash.bashrc
RUN echo 'dev ALL=(ALL) NOPASSWD: /bin/crontab' | EDITOR='tee -a' visudo
RUN sed -i 's/test -r /test -e /g' /etc/profile
RUN mkdir -p /webcrate; \
    mkdir -p /webcrate-bin; \
    mkdir -p /webcrate-bin/php; \
    ln -s /bin/php /webcrate-bin/php/php; \
    mkdir -p /webcrate-fish; \
    chmod o-rwx /webcrate;
WORKDIR /webcrate-fish
RUN git clone https://github.com/oh-my-fish/oh-my-fish
WORKDIR /webcrate-fish/oh-my-fish
RUN bin/install --offline --path=/webcrate-fish/omf --noninteractive --config=/webcrate-fish/omfconf; \
    cp /root/.config/fish/conf.d/omf.fish /etc/fish/conf.d/omf.fish; \
    fish -C "omf install cbjohnson"; \
    cp /webcrate-fish/omf/themes/default/functions/fish_right_prompt.fish /webcrate-fish/omf/themes/cbjohnson/fish_right_prompt.fish;
COPY fish_prompt.fish /webcrate-fish/omf/themes/cbjohnson/fish_prompt.fish
WORKDIR /root
RUN rm /etc/php/conf.d/imagick.ini; \
    rm /etc/php/conf.d/xdebug.ini; \
    yes | sudo symfony self-update;

WORKDIR /
RUN mkdir -p /webcrate-telegraf; \
    chown telegraf:telegraf /webcrate-telegraf; \
    chmod o-rwx /webcrate-telegraf;

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
    chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
