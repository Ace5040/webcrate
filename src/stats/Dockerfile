FROM archlinux:base-20241027.0.273886

#install and add user
RUN pacman --needed --noconfirm -Syu; \
    pacman --needed --noconfirm -S base-devel git unzip python python-pip docker; \
    yes | pacman -Scc; \
    useradd -m -s /bin/bash dev; \
    usermod -p "dev" dev; \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo; \
    sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j12\"/g" /etc/makepkg.conf

USER dev
WORKDIR /home/dev

#install telegraf-bin
RUN git clone https://aur.archlinux.org/telegraf-bin.git && \
    cd telegraf-bin && \
    makepkg -scir --nocheck --noconfirm --skipchecksums && \
    rm -rf /home/dev/telegraf-bin

#install docker-systemctl-replacement-git
RUN git clone https://aur.archlinux.org/docker-systemctl-replacement-git.git; \
    cd docker-systemctl-replacement-git; \
    makepkg -scir --nocheck --noconfirm --skipchecksums; \
    rm -rf /home/dev/docker-systemctl-replacement-git.git

USER root
RUN systemctl enable telegraf;
RUN rm -f /etc/telegraf/telegraf.conf;
RUN rm -f /etc/telegraf/telegraf.conf;
RUN sed -i "s/User=telegraf/User=root/g" /usr/lib/systemd/system/telegraf.service

RUN chown root:root /bin/systemctl.py; \
    chmod a+x /bin/systemctl.py; \
    mv /bin/systemctl /bin/systemctl_original; \
    cp /bin/systemctl.py /bin/systemctl
WORKDIR /
COPY ["telegraf.conf", "/etc/telegraf/"]
COPY ["entrypoint.sh", "/"]
RUN chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
