ARG IMAGE
FROM $IMAGE
RUN apt-get update && \
    apt-get --assume-yes --no-install-recommends install sudo && \
    rm -rf /var/lib/apt/lists/*
COPY entrypoint.sh /entrypoint.sh
RUN chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
