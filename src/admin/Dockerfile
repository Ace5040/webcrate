FROM archlinux:latest

#update pacman db
RUN pacman --needed --noconfirm -Syu; \
    pacman --needed --noconfirm -S fakeroot binutils git nano openssh unzip composer npm mariadb-clients iputils inetutils which python-pip nginx docker \
    php php-fpm php-intl php-sqlite php-gd php-xsl php-tidy php-imagick php-memcached

#make automake bison binutils autoconf gcc patch
RUN pacman --needed --noconfirm -S sudo;
RUN useradd -m -s /bin/bash dev
RUN useradd -m -s /bin/bash app
RUN usermod -p "dev" dev
RUN usermod -u 555 dev
RUN groupmod -g 555 dev
RUN echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo
RUN sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j6\"/g" /etc/makepkg.conf

USER dev
WORKDIR /home/dev

#install symfony-cli-bin
RUN git clone https://aur.archlinux.org/symfony-cli-bin.git; \
    cd symfony-cli-bin; \
    makepkg -scir --nocheck --noconfirm --skipchecksums

#install docker-systemctl-replacement-git
RUN git clone https://aur.archlinux.org/docker-systemctl-replacement-git.git; \
    cd docker-systemctl-replacement-git; \
    makepkg -scir --nocheck --noconfirm --skipchecksums

USER root

RUN python -m ensurepip --upgrade; \
    pip3 install --upgrade pip; \
    pip install pyyml munch; \
    chown root:root /bin/systemctl.py; \
    chmod a+x /bin/systemctl.py; \
    mv /bin/systemctl /bin/systemctl_original; \
    cp /bin/systemctl.py /bin/systemctl; \
    systemctl enable php-fpm; \
    systemctl enable nginx; \
    sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php/php.ini; \
    sed -i "s/; extension = imagick/extension=imagick/g" /etc/php/conf.d/imagick.ini;
COPY pool.conf /etc/php/php-fpm.d/pool.conf
COPY php.ini /etc/php/conf.d/user.ini
RUN echo 'app ALL=(ALL) NOPASSWD: /webcrate/versions.py' | EDITOR='tee -a' visudo; \
    echo 'app ALL=(ALL) NOPASSWD: /webcrate/updateprojects.py' | EDITOR='tee -a' visudo; \
    echo 'app ALL=(ALL) NOPASSWD: /webcrate/reload.py' | EDITOR='tee -a' visudo
COPY app /app
RUN mkdir /webcrate; \
    chown app:app /webcrate; \
    chown -R app:app /app
WORKDIR /app
USER app
RUN composer config --no-plugins allow-plugins.symfony/flex true; \
    sed -i "s/.*\"@auto-scripts\".*/ /g" composer.json; \
    rm -f composer.lock; \
    composer install --no-scripts
WORKDIR /app/assets/admin
RUN npm install; \
    NODE_OPTIONS=--openssl-legacy-provider npm run build
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
