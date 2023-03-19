FROM archlinux:latest

#install system utils and services
RUN pacman --needed --noconfirm -Syu && \
    pacman --needed --noconfirm -S git nano openssh base-devel unzip composer npm mc iputils cronie inetutils wget tmux ruby python-pip python-virtualenv fish exim postgresql-libs libjpeg gunicorn && \
    yes | pacman -Scc && \
    useradd -m -s /bin/bash dev && \
    usermod -p "dev" dev && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo && \
    sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j6\"/g" /etc/makepkg.conf;

WORKDIR /home/dev
USER dev

#install docker-systemctl-replacement-git
RUN git clone https://aur.archlinux.org/docker-systemctl-replacement-git.git && \
    cd docker-systemctl-replacement-git && \
    makepkg -scir --nocheck --noconfirm --skipchecksums && \
    rm -rf /home/dev/docker-systemctl-replacement-git

#misc install and config
USER root
WORKDIR /root
RUN gem install compass --norc && \
    pip install pyyml munch && \
    chown root:root /bin/systemctl.py && \
    chmod a+x /bin/systemctl.py && \
    mv /bin/systemctl /bin/systemctl_original && \
    cp /bin/systemctl.py /bin/systemctl && \
    ssh-keygen -A && \
    systemctl enable sshd && \
    systemctl enable cronie && \
    systemctl enable exim && \
    sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/g" /etc/ssh/sshd_config && \
    sed -i "s/#StrictModes yes/StrictModes no/g" /etc/ssh/sshd_config && \
    echo ". /etc/profile.d/bashrc.sh" >> /etc/bash.bashrc && \
    echo 'dev ALL=(ALL) NOPASSWD: /bin/crontab' | EDITOR='tee -a' visudo && \
    sed -i 's/test -r /test -e /g' /etc/profile && \
    mkdir -p /webcrate && \
    mkdir -p /webcrate-bin && \
    mkdir -p /webcrate-fish && \
    chmod o-rwx /webcrate;

#install fish
WORKDIR /webcrate-fish/oh-my-fish
RUN git clone https://github.com/oh-my-fish/oh-my-fish . && \
    bin/install --offline --path=/webcrate-fish/omf --noninteractive --config=/webcrate-fish/omfconf && \
    rm -rf ./* && \
    cp /root/.config/fish/conf.d/omf.fish /etc/fish/conf.d/omf.fish && \
    fish -C "omf install cbjohnson" && \
    cp /webcrate-fish/omf/themes/default/functions/fish_right_prompt.fish /webcrate-fish/omf/themes/cbjohnson/fish_right_prompt.fish;
COPY fish_prompt.fish /webcrate-fish/omf/themes/cbjohnson/fish_prompt.fish

WORKDIR /
#copy scripts
COPY ["fishrc.fish", "/etc/fish/conf.d/"]
COPY ["bashrc.sh", "/etc/profile.d/"]
COPY ["gunicorn_restart.sh", "/webcrate-bin/"]
COPY ["versions.py", "parse-projects.py", "sync_ssh_keys.sh", "log.py", "/webcrate/"]
COPY ["entrypoint.sh", "/"]
RUN chmod u+x /webcrate/sync_ssh_keys.sh && \
    rm /etc/mail/exim.conf && \
    chmod a+x /webcrate-bin/gunicorn_restart.sh && \
    chmod u+x /webcrate/parse-projects.py && \
    chmod u+x /webcrate/versions.py && \
    chmod u+s /bin/ping && \
    chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
