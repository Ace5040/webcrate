FROM archlinux:latest

#install system utils and services
RUN pacman --needed --noconfirm -Syu && \
    pacman --needed --noconfirm -S git base-devel unzip python-pip && \
    yes | pacman -Scc && \
    useradd -m -s /bin/bash dev && \
    usermod -p "dev" dev && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo && \
    sed -i "s/#MAKEFLAGS=\"-j6\"/MAKEFLAGS=\"-j12\"/g" /etc/makepkg.conf

USER dev
WORKDIR /home/dev

#install docker-systemctl-replacement-git
RUN git clone https://aur.archlinux.org/docker-systemctl-replacement-git.git && \
    cd docker-systemctl-replacement-git && \
    makepkg -scir --nocheck --noconfirm --skipchecksums

#install proftpd
RUN git clone https://aur.archlinux.org/proftpd.git && \
    cd proftpd && \
    makepkg -scir --nocheck --noconfirm --skipchecksums

USER root

#install phyton libs
RUN pip install --break-system-packages pyyml munch setuptools && \
    chown root:root /bin/systemctl.py && \
    chmod a+x /bin/systemctl.py && \
    mv /bin/systemctl /bin/systemctl_original && \
    cp /bin/systemctl.py /bin/systemctl && \
    systemctl enable proftpd && \
    mkdir -p /webcrate

WORKDIR /
COPY ["proftpd.conf", "/etc/"]
COPY ["parse-projects.py", "log.py", "/webcrate/"]
COPY ["entrypoint.sh", "/"]
RUN chmod u+x /webcrate/parse-projects.py && \
    chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
EXPOSE 21/tcp
EXPOSE 20/udp
EXPOSE 50000-60000/udp
