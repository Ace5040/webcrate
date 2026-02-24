ARG IMAGE=debian:bookworm-slim
FROM $IMAGE

RUN sed -i "s/deb.debian.org/mirror.truenetwork.ru/g" /etc/apt/sources.list.d/debian.sources
RUN apt-get update
RUN apt-get --assume-yes install sudo git \
    unzip wget curl supervisor \
    python3 python3-pip python3-yaml python3-munch

RUN curl --silent --location -O https://repos.influxdata.com/influxdata-archive.key
RUN gpg --show-keys --with-fingerprint --with-colons ./influxdata-archive.key 2>&1 \
    | grep -q '^fpr:\+24C975CBA61A024EE1B631787C3D57159FC2F927:$' \
    && cat influxdata-archive.key \
    | gpg --dearmor \
    | tee /etc/apt/keyrings/influxdata-archive.gpg > /dev/null \
    && echo 'deb [signed-by=/etc/apt/keyrings/influxdata-archive.gpg] https://repos.influxdata.com/debian stable main' \
    | tee /etc/apt/sources.list.d/influxdata.list

RUN apt-get update && apt-get --assume-yes install telegraf

RUN usermod -s /bin/bash root

RUN adduser --no-create-home --disabled-login -shell /bin/bash dev && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

RUN rm -f /etc/telegraf/telegraf.conf;

WORKDIR /
COPY ["telegraf.conf", "/etc/telegraf/"]
COPY ["entrypoint.sh", "supervisord.conf.template", "/"]
RUN chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
