FROM archlinux:latest

#install and add user
RUN pacman --needed --noconfirm -Syu; \
    pacman --needed --noconfirm -S base-devel git unzip mariadb-clients postgresql-libs cronie python python-pip certbot duplicity lftp pwgen docker; \
    yes | pacman -Scc; \
    useradd -m -s /bin/bash dev; \
    usermod -p "dev" dev; \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo; \
    sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j6\"/g" /etc/makepkg.conf

USER dev
WORKDIR /home/dev

#install docker-systemctl-replacement-git
RUN git clone https://aur.archlinux.org/docker-systemctl-replacement-git.git; \
    cd docker-systemctl-replacement-git; \
    makepkg -scir --nocheck --noconfirm --skipchecksums; \
    rm -rf /home/dev/docker-systemctl-replacement-git.git

USER root

RUN pip install pyyml munch
RUN chown root:root /bin/systemctl.py; \
    chmod a+x /bin/systemctl.py; \
    mv /bin/systemctl /bin/systemctl_original; \
    cp /bin/systemctl.py /bin/systemctl
RUN systemctl enable cronie;
WORKDIR /
RUN mkdir -p /webcrate;
COPY ["pwgen.sh", "ssl.conf", "gzip.conf", "redirect.conf", "/webcrate/"]
COPY ["entrypoint.sh", "/"]
COPY scripts /webcrate/scripts
RUN chmod -R u+x /webcrate/scripts; \
    chmod u+x /webcrate/pwgen.sh; \
    chmod u+x /entrypoint.sh
RUN echo '0 6 * * 1 root . /docker.env; /webcrate/scripts/certbot-renew.py' > /etc/cron.d/certbot-renew
RUN echo '0 3 * * * root . /docker.env; /webcrate/scripts/backup.py' > /etc/cron.d/backup
WORKDIR /webcrate
CMD ["/entrypoint.sh"]
