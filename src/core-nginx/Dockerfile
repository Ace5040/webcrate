ARG IMAGE
FROM $IMAGE
RUN apt-get update
RUN apt-get --assume-yes install sudo
COPY entrypoint.sh /entrypoint.sh
RUN chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
