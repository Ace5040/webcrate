FROM archlinux:latest
RUN echo "Set disable_coredump false" >> /etc/sudo.conf
RUN pacman --noconfirm -Syu
RUN pacman --needed --noconfirm -S mc certbot
RUN useradd -m -s /bin/bash dev
RUN usermod -p "dev" dev
RUN mkdir -p /sitesbox
COPY generate_hosts.sh /sitesbox/generate_hosts.sh
RUN chmod u+x /sitesbox/generate_hosts.sh
COPY generate_configs.sh /sitesbox/generate_configs.sh
RUN chmod u+x /sitesbox/generate_configs.sh
COPY generate_pool.sh /sitesbox/generate_pool.sh
RUN chmod u+x /sitesbox/generate_pool.sh
