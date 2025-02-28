ARG IMAGE=debian:trixie-slim
FROM $IMAGE

RUN sed -i "s/deb.debian.org/mirror.truenetwork.ru/g" /etc/apt/sources.list.d/debian.sources
RUN apt-get update
RUN apt-get --assume-yes install sudo git \
    unzip wget curl supervisor \
    python3 python3-pip python3-yaml python3-munch

RUN echo deb https://repos.influxdata.com/debian bookworm stable > /etc/apt/sources.list.d/influxdata.list

RUN curl -fsSL https://repos.influxdata.com/influxdata-archive_compat.key|sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/influxdata.gpg

RUN apt-get update && \
    apt-get --assume-yes install telegraf

RUN usermod -s /bin/bash root

RUN adduser --no-create-home --disabled-login -shell /bin/bash dev && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

RUN rm -f /etc/telegraf/telegraf.conf;
# RUN sed -i "s/User=telegraf/User=root/g" /usr/lib/systemd/system/telegraf.service

WORKDIR /
COPY ["telegraf.conf", "/etc/telegraf/"]
COPY ["entrypoint.sh", "supervisord.conf.template", "/"]
RUN chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
