ARG IMAGE_NGINX_BASE
FROM $IMAGE_NGINX_BASE
RUN apt-get update
RUN apt-get --assume-yes install sudo
COPY entrypoint.sh /entrypoint.sh
RUN chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
