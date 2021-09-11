FROM archlinux:latest

#update pacman db
RUN pacman --needed --noconfirm -Syu

#install system utils and services
RUN pacman --needed --noconfirm -S base-devel git unzip mariadb-clients postgresql-libs cronie python python-pip certbot duplicity lftp pwgen docker;

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
RUN yay --gpgflags "--keyserver hkp://keyserver.ubuntu.com" --noeditmenu --nodiffmenu --noconfirm --mflags --nocheck -S docker-systemctl-replacement-git

USER root

RUN pip install pyyml munch
RUN chown root:root /bin/systemctl.py; \
    chmod a+x /bin/systemctl.py; \
    mv /bin/systemctl /bin/systemctl_original; \
    cp /bin/systemctl.py /bin/systemctl
RUN systemctl enable cronie;
WORKDIR /
RUN mkdir -p /webcrate;
COPY ["ssl.conf", "gzip.conf", "gzip.conf", "redirect.conf", "parse-configs.py", "parse-projects.py", "parse-services.py", "certbot-renew.py", "certbot-renew-deploy.py", "backup.py", "/webcrate/"]
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
