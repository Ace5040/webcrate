FROM alpine:3.17
RUN apk update &&\
    apk add \
    docker \
    cronie \
    certbot \
    duplicity \
    lftp \
    pwgen \
    openssl \
    mariadb-client \
    python3 py3-yaml py3-idna py3-munch \
    postgresql-client &&\
    rm -rf /var/cache/apk/*
RUN mkdir /webcrate
COPY [ \
    "entrypoint.sh", \
    "pwgen.sh", \
    "gzip.conf", \
    "redirect-ssl.conf", \
    "redirect.conf", \
    "ssl.conf", \
    "helpers.py", \
    "parse-projects.py", \
    "project-config.py", \
    "project-start.py", \
    "parse-redirects.py", \
    "redirect-config.py", \
    "redirect-start.py", \
    "parse-services.py", \
    "services-init.py", \
    "log.py", \
    "backup.py", \
    "certbot-renew-deploy.py", \
    "certbot-renew.py", \
    "/" \
]
COPY [ \
    "gzip.conf", \
    "redirect-ssl.conf", \
    "redirect.conf", \
    "ssl.conf", \
    "/webcrate" \
]
RUN chmod u+x /*.py &&\
    chmod u+x /pwgen.sh &&\
    chmod u+x /entrypoint.sh
RUN echo '0 6 * * 1 root . /docker.env; /certbot-renew.py' > /etc/cron.d/certbot-renew && \
    echo '0 3 * * * root . /docker.env; /backup.py' > /etc/cron.d/backup

CMD ["/entrypoint.sh"]
