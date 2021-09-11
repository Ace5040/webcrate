FROM archlinux:latest

#update pacman db
RUN pacman --needed --noconfirm -Syu

#install system utils and services
RUN pacman --needed --noconfirm -S git nano openssh base-devel unzip composer npm mariadb-clients iputils inetutils which python-pip nginx docker

#install latest php
RUN pacman --needed --noconfirm -S php php-fpm php-intl php-sqlite php-gd php-xsl php-tidy php-imagick php-memcached

RUN useradd -m -s /bin/bash dev
RUN useradd -m -s /bin/bash app
RUN usermod -p "dev" dev
RUN usermod -u 555 dev
RUN groupmod -g 555 dev
RUN echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo
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
RUN yay --gpgflags "--keyserver hkp://keyserver.ubuntu.com" --noeditmenu --nodiffmenu --noconfirm --mflags --nocheck -S docker-systemctl-replacement-git symfony-cli

USER root

RUN pip install pyyml munch
RUN chown root:root /bin/systemctl.py
RUN chmod a+x /bin/systemctl.py
RUN mv /bin/systemctl /bin/systemctl_original
RUN cp /bin/systemctl.py /bin/systemctl
RUN systemctl enable php-fpm;
RUN systemctl enable nginx;
RUN sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php/php.ini; \
    sed -i "s/; extension = imagick/extension=imagick/g" /etc/php/conf.d/imagick.ini;
RUN yes | sudo symfony self-update
COPY pool.conf /etc/php/php-fpm.d/pool.conf
COPY php.ini /etc/php/conf.d/user.ini
RUN echo 'app ALL=(ALL) NOPASSWD: /webcrate/versions.py' | EDITOR='tee -a' visudo
RUN echo 'app ALL=(ALL) NOPASSWD: /webcrate/updateprojects.py' | EDITOR='tee -a' visudo
RUN echo 'app ALL=(ALL) NOPASSWD: /webcrate/reload.py' | EDITOR='tee -a' visudo
COPY app /app
RUN mkdir /webcrate; \
    chown app:app /webcrate; \
    chown -R app:app /app
WORKDIR /app
USER app
RUN sed -i "s/.*\"@auto-scripts\".*/ /g" composer.json;
RUN rm -f composer.lock
RUN composer install --no-scripts
WORKDIR /app/assets/admin
RUN npm install
RUN npm run build
USER root
COPY init-db.py /webcrate/init-db.py
COPY nginx.conf /etc/nginx/nginx.conf
COPY versions.py /webcrate/versions.py
COPY updateprojects.py /webcrate/updateprojects.py
COPY reload.py /webcrate/reload.py
COPY entrypoint.sh /entrypoint.sh
CMD ["/entrypoint.sh"]
RUN chmod u+x /webcrate/init-db.py; \
    chmod a+rxs /webcrate/versions.py; \
    chmod a+rxs /webcrate/updateprojects.py; \
    chmod a+rxs /webcrate/reload.py; \
    chmod u+x /entrypoint.sh
