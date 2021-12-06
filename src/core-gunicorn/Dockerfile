FROM archlinux:latest

#install system utils and services
RUN pacman --needed --noconfirm -Syu; \
    pacman --needed --noconfirm -S git nano openssh base-devel unzip composer npm mc iputils cronie inetutils wget tmux ruby python-pip python-virtualenv fish exim postgresql-libs libjpeg; \
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
RUN yay --gpgflags "--keyserver hkp://keyserver.ubuntu.com" --noeditmenu --nodiffmenu --noconfirm --mflags --nocheck -S docker-systemctl-replacement-git telegraf-bin gunicorn; \
    yes | yay -Scc; \
    rm -rf /home/dev/.cache

#misc install and config
USER root
WORKDIR /root
RUN gem install compass --norc; \
    pip install pyyml munch; \
    chown root:root /bin/systemctl.py; \
    chmod a+x /bin/systemctl.py; \
    mv /bin/systemctl /bin/systemctl_original; \
    cp /bin/systemctl.py /bin/systemctl; \
    ssh-keygen -A; \
    systemctl enable sshd; \
    systemctl enable cronie; \
    systemctl enable telegraf; \
    systemctl enable exim; \
    sed -i "s/# urls = \[\"http\:\/\/127\.0\.0\.1\:8086\"\]/urls = \[\"http\:\/\/influxdb\:8086\"\]/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/# skip_database_creation = false/skip_database_creation = true/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/# database = \"telegraf\"/database = \"telegraf\"/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/g" /etc/ssh/sshd_config; \
    sed -i "s/#StrictModes yes/StrictModes no/g" /etc/ssh/sshd_config; \
    echo ". /etc/profile.d/bashrc.sh" >> /etc/bash.bashrc; \
    echo 'dev ALL=(ALL) NOPASSWD: /bin/crontab' | EDITOR='tee -a' visudo; \
    sed -i 's/test -r /test -e /g' /etc/profile; \
    mkdir -p /webcrate; \
    mkdir -p /webcrate-bin; \
    mkdir -p /webcrate-fish; \
    chmod o-rwx /webcrate; \
    mkdir -p /webcrate-telegraf; \
    chown telegraf:telegraf /webcrate-telegraf; \
    chmod o-rwx /webcrate-telegraf;

#install fish
WORKDIR /webcrate-fish/oh-my-fish
RUN git clone https://github.com/oh-my-fish/oh-my-fish .; \
    bin/install --offline --path=/webcrate-fish/omf --noninteractive --config=/webcrate-fish/omfconf; \
    rm -rf ./*; \
    cp /root/.config/fish/conf.d/omf.fish /etc/fish/conf.d/omf.fish; \
    fish -C "omf install cbjohnson"; \
    cp /webcrate-fish/omf/themes/default/functions/fish_right_prompt.fish /webcrate-fish/omf/themes/cbjohnson/fish_right_prompt.fish;
COPY fish_prompt.fish /webcrate-fish/omf/themes/cbjohnson/fish_prompt.fish

WORKDIR /
#copy scripts
COPY ["toprc", "/etc/telegraf/.config/procps/"]
COPY ["fishrc.fish", "/etc/fish/conf.d/"]
COPY ["bashrc.sh", "/etc/profile.d/"]
COPY ["stats_projects.sh", "stats_pools.sh", "/webcrate-telegraf/"]
COPY ["gunicorn_restart.sh", "/webcrate-bin/"]
COPY ["versions.py", "parse-projects.py", "sync_ssh_keys.sh", "log.py", "/webcrate/"]
COPY ["entrypoint.sh", "/"]
RUN chmod u+x /webcrate/sync_ssh_keys.sh; \
    chmod a+x /webcrate-telegraf/stats_projects.sh; \
    chmod a+x /webcrate-telegraf/stats_pools.sh; \
    mkdir -p /etc/telegraf/.config/procps; \
    rm /etc/mail/exim.conf; \
    chmod a+x /webcrate-bin/gunicorn_restart.sh; \
    chmod u+x /webcrate/parse-projects.py; \
    chmod u+x /webcrate/versions.py; \
    chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
