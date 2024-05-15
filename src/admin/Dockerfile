FROM archlinux:latest

RUN sed -Ei "s/default mirrors./default mirrors.\n\n[home_el_archphp_Arch]\nServer = https:\/\/download.opensuse.org\/repositories\/home:\/el:\/archphp\/Arch\/\$arch/g" /etc/pacman.conf && \
    key=$(curl -fsSL https://download.opensuse.org/repositories/home:el:archphp/Arch/$(uname -m)/home_el_archphp_Arch.key) && \
    fingerprint=$(gpg --quiet --with-colons --import-options show-only --import --fingerprint <<< "${key}" | awk -F: '$1 == "fpr" { print $10 }') && \
    pacman-key --init && \
    pacman-key --add - <<< "${key}" && \
    pacman-key --lsign-key "${fingerprint}"

#update pacman db
RUN pacman --needed --noconfirm -Syu && \
    pacman --needed --noconfirm -S sudo wget pcre debugedit fakeroot binutils git nano openssh unzip npm mariadb-clients iputils inetutils which python-yaml python-munch python-setuptools nginx docker && \
    yes | pacman -Scc

#install php74
RUN pacman --needed --noconfirm -S php74 php74-fileinfo php74-ctype php74-json php74-pecl php74-pear php74-zip php74-xmlreader php74-xmlwriter php74-mbstring php74-openssl php74-xml php74-fpm php74-intl php74-sqlite php74-gd php74-xsl php74-simplexml php74-phar php74-tidy php74-cli php74-tokenizer php74-curl php74-opcache php74-iconv php74-mysql php74-pdo php74-soap php74-imagick

#add dev user
RUN useradd -m -s /bin/bash dev && \
    usermod -p "dev" dev && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo && \
    sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j12\"/g" /etc/makepkg.conf
USER dev
WORKDIR /home/dev

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
RUN chown root:root /bin/systemctl.py && \
    chmod a+x /bin/systemctl.py && \
    wget -O composer.phar https://getcomposer.org/download/latest-stable/composer.phar && \
    chmod +x composer.phar && \
    mv composer.phar /usr/bin/composer && \
    mv /bin/systemctl /bin/systemctl_original && \
    cp /bin/systemctl.py /bin/systemctl && \
    systemctl enable php74-fpm && \
    systemctl enable nginx && \
    ln -s /bin/php74 /bin/php && \
    sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php74/php.ini
COPY pool.conf /etc/php74/php-fpm.d/pool.conf
COPY php.ini /etc/php74/conf.d/user.ini
RUN echo 'dev ALL=(ALL) NOPASSWD: /webcrate/versions.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/updateprojects.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/updateredirects.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/reload-redirect.py' | EDITOR='tee -a' visudo && \
    echo 'dev ALL=(ALL) NOPASSWD: /webcrate/reload.py' | EDITOR='tee -a' visudo
COPY app /app
RUN mkdir /webcrate && \
    chown dev:dev /webcrate && \
    chown -R dev:dev /app
WORKDIR /app
USER dev

RUN rm -f composer.lock && \
    composer install --no-scripts

WORKDIR /app/assets/admin
RUN npm install --verbose && \
    NODE_OPTIONS=--openssl-legacy-provider npm run build
USER root
COPY ["init-db.py", "log.py", "updateprojects.py", "updateredirects.py", "reload-redirect.py", "versions.py", "reload.py", "/webcrate"]
COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh
CMD ["/entrypoint.sh"]
RUN chmod u+x /webcrate/init-db.py && \
    chmod a+rxs /webcrate/log.py && \
    chmod a+rxs /webcrate/versions.py && \
    chmod a+rxs /webcrate/updateprojects.py && \
    chmod a+rxs /webcrate/updateredirects.py && \
    chmod a+rxs /webcrate/reload.py && \
    chmod a+rxs /webcrate/reload-redirect.py && \
    chmod u+x /entrypoint.sh
EXPOSE 80
