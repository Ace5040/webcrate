FROM archlinux:latest
RUN echo "Set disable_coredump false" >> /etc/sudo.conf
RUN pacman --noconfirm -Syu
RUN pacman --needed --noconfirm -S git nano openssh base-devel unzip composer npm mariadb-clients iputils inetutils which python-pip
RUN pacman --needed --noconfirm -S php php-fpm php-intl php-sqlite php-gd php-xsl php-intl php-tidy php-imagick php-memcached
RUN pacman --needed --noconfirm -S nginx
RUN useradd -m -s /bin/bash dev
RUN useradd -m -s /bin/bash app
RUN usermod -p "dev" dev
RUN echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo
RUN sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j6\"/g" /etc/makepkg.conf
USER dev
WORKDIR /home/dev
RUN git clone https://aur.archlinux.org/yay.git
WORKDIR /home/dev/yay
RUN makepkg -scir --noconfirm
WORKDIR /home/dev
RUN gpg --keyserver keys.gnupg.net --recv-key 32E4B74757B1D65234FC389F293D771241515FE8
RUN yay --noeditmenu --nodiffmenu --noconfirm -S docker docker-systemctl-replacement-git symfony-cli
USER root
RUN pip install pyyml munch
RUN chown root:root /bin/systemctl.py
RUN chmod a+x /bin/systemctl.py
RUN mv /bin/systemctl /bin/systemctl_original
RUN cp /bin/systemctl.py /bin/systemctl
RUN systemctl enable php-fpm;
RUN systemctl enable nginx;
RUN sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php/php.ini; \
    sed -i "s/;extension=imagick/extension=imagick/g" /etc/php/conf.d/imagick.ini;
RUN yes | sudo symfony self-update
COPY pool.conf /etc/php/php-fpm.d/pool.conf
COPY php.ini /etc/php/conf.d/user.ini
COPY entrypoint.sh /entrypoint.sh
RUN chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
RUN mkdir /app; \
    chown app:app /app
USER app
WORKDIR /app
RUN git clone https://github.com/Ace5040/webcrate-admin.git .
RUN sed -i "s/.*\"@auto-scripts\".*/ /g" composer.json;
RUN composer install --no-scripts
RUN npm install
RUN npm run build
USER root
RUN echo 'app ALL=(ALL) NOPASSWD: /webcrate/versions.py' | EDITOR='tee -a' visudo
COPY init-db.py /webcrate/init-db.py
RUN chmod u+x /webcrate/init-db.py
COPY nginx.conf /etc/nginx/nginx.conf
COPY versions.py /webcrate/versions.py
RUN chmod a+rxs /webcrate/versions.py