ARG IMAGE=debian:bookworm-slim
FROM $IMAGE

RUN sed -i "s/deb.debian.org/mirror.truenetwork.ru/g" /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get --assume-yes --no-install-recommends install \
        sudo git unzip wget curl supervisor \
        python3 python3-pip python3-yaml python3-munch \
        gpg && \
    rm -rf /var/lib/apt/lists/*

RUN usermod -s /bin/bash root && \
    adduser --no-create-home --disabled-login -shell /bin/bash dev && \
    echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

# Install telegraf
RUN mkdir -p /etc/apt/keyrings && \
    curl --silent --location -O https://repos.influxdata.com/influxdata-archive.key && \
    gpg --show-keys --with-fingerprint --with-colons ./influxdata-archive.key 2>&1 \
        | grep -q '^fpr:\+24C975CBA61A024EE1B631787C3D57159FC2F927:$' && \
    cat influxdata-archive.key | gpg --dearmor | tee /etc/apt/keyrings/influxdata-archive.gpg > /dev/null && \
    echo 'deb [signed-by=/etc/apt/keyrings/influxdata-archive.gpg] https://repos.influxdata.com/debian stable main' \
        > /etc/apt/sources.list.d/influxdata.list && \
    rm influxdata-archive.key && \
    apt-get update && \
    apt-get --assume-yes --no-install-recommends install telegraf && \
    rm -rf /var/lib/apt/lists/* /etc/telegraf/telegraf.conf

WORKDIR /
COPY ["telegraf.conf", "/etc/telegraf/"]
COPY ["entrypoint.sh", "supervisord.conf.template", "/"]
RUN chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
