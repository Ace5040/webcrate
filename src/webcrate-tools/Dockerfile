FROM archlinux:latest
RUN echo "Set disable_coredump false" >> /etc/sudo.conf
RUN pacman --noconfirm -Syu; \
    pacman --needed --noconfirm -S base-devel git unzip mariadb-clients postgresql-libs cronie python python-pip certbot duplicity lftp pwgen;
RUN useradd -m -s /bin/bash dev; \
    usermod -p "dev" dev; \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo
RUN sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j6\"/g" /etc/makepkg.conf
USER dev
WORKDIR /home/dev
RUN git clone https://aur.archlinux.org/yay.git
WORKDIR /home/dev/yay
RUN makepkg -scir --noconfirm
WORKDIR /home/dev
RUN yay --noeditmenu --nodiffmenu --noconfirm -S docker-systemctl-replacement-git docker
USER root
RUN pip install pyyml munch
RUN chown root:root /bin/systemctl.py; \
    chmod a+x /bin/systemctl.py; \
    mv /bin/systemctl /bin/systemctl_original; \
    cp /bin/systemctl.py /bin/systemctl
RUN systemctl enable cronie;
WORKDIR /
RUN mkdir -p /webcrate;
COPY ssl.conf /webcrate/ssl.conf
COPY gzip.conf /webcrate/gzip.conf
COPY redirect.conf /webcrate/redirect.conf
COPY parse-configs.py /webcrate/parse-configs.py
COPY parse-projects.py /webcrate/parse-projects.py
COPY parse-services.py /webcrate/parse-services.py
COPY certbot-renew.py /webcrate/certbot-renew.py
COPY certbot-renew-deploy.py /webcrate/certbot-renew-deploy.py
COPY backup.py /webcrate/backup.py
COPY entrypoint.sh /entrypoint.sh
COPY pwgen.sh /webcrate/pwgen.sh
RUN chmod a+x /webcrate/parse-configs.py; \
    chmod a+x /webcrate/parse-projects.py; \
    chmod a+x /webcrate/parse-services.py; \
    chmod a+x /webcrate/certbot-renew.py; \
    chmod a+x /webcrate/certbot-renew-deploy.py; \
    chmod a+x /webcrate/backup.py; \
    chmod u+x /webcrate/pwgen.sh; \
    chmod u+x /entrypoint.sh
#RUN echo '*/10 * * * * root . /docker.env; /webcrate/parse-configs.py;' > /etc/cron.d/parse-configs
RUN echo '0 6 * * 1 root . /docker.env; /webcrate/certbot-renew.py' > /etc/cron.d/certbot-renew
RUN echo '0 3 * * * root . /docker.env; /webcrate/backup.py' > /etc/cron.d/backup
WORKDIR /webcrate
CMD ["/entrypoint.sh"]
