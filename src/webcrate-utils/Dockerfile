FROM archlinux:latest
RUN echo "Set disable_coredump false" >> /etc/sudo.conf
RUN pacman --noconfirm -Syu
RUN pacman --needed --noconfirm -S mc certbot
RUN pacman --needed --noconfirm -S python python-pip
RUN pip install pyyml munch
RUN useradd -m -s /bin/bash dev
RUN usermod -p "dev" dev
RUN mkdir -p /webcrate
COPY parse-users.py /webcrate/parse-users.py
RUN chmod u+x /webcrate/parse-users.py
