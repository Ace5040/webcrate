FROM archlinux:latest
RUN echo "Set disable_coredump false" >> /etc/sudo.conf
RUN pacman --noconfirm -Syu
RUN pacman --needed --noconfirm -S mc certbot pwgen python python-pip
RUN pip install pyyml munch
RUN mkdir -p /webcrate
COPY ssl.conf /webcrate/ssl.conf
COPY redirect.conf /webcrate/redirect.conf
COPY gzip.conf /webcrate/gzip.conf
COPY parse-users.py /webcrate/parse-users.py
COPY parse-services.py /webcrate/parse-services.py
COPY create-user.py /webcrate/create-user.py
COPY pwgen.sh /webcrate/pwgen.sh
RUN chmod u+x /webcrate/parse-users.py; \
    chmod u+x /webcrate/parse-services.py; \
    chmod u+x /webcrate/create-user.py; \
    chmod u+x /webcrate/pwgen.sh
