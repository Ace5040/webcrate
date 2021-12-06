FROM archlinux:latest

#install system utils and services
RUN pacman --needed --noconfirm -Syu; \
    pacman --needed --noconfirm -S git base-devel unzip python-pip; \
    yes | pacman -Scc; \
    useradd -m -s /bin/bash dev; \
    usermod -p "dev" dev; \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo; \
    sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j6\"/g" /etc/makepkg.conf

#install yay
WORKDIR /home/dev/yay
RUN chown dev:dev /home/dev/yay
USER dev
RUN git clone https://aur.archlinux.org/yay.git .; \
    makepkg -scir --noconfirm; \
    rm -rf /home/dev/yay

#install aur packages
RUN yay --gpgflags "--keyserver hkp://keyserver.ubuntu.com" --noeditmenu --nodiffmenu --noconfirm --mflags --nocheck -S docker-systemctl-replacement-git proftpd; \
    yes | yay -Scc; \
    rm -rf /home/dev/.cache

USER root

#install phyton libs
RUN pip install pyyml munch; \
    chown root:root /bin/systemctl.py; \
    chmod a+x /bin/systemctl.py; \
    mv /bin/systemctl /bin/systemctl_original; \
    cp /bin/systemctl.py /bin/systemctl; \
    systemctl enable proftpd; \
    mkdir -p /webcrate

WORKDIR /
COPY ["proftpd.conf", "/etc/"]
COPY ["parse-projects.py", "log.py", "/webcrate/"]
COPY ["entrypoint.sh", "/"]
RUN chmod u+x /webcrate/parse-projects.py; \
    chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
