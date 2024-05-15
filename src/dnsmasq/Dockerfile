FROM alpine:latest

RUN apk update
RUN apk add --no-cache dnsmasq-dnssec
RUN sed -i "s/local-service/#local-service/g" /etc/dnsmasq.conf
COPY ["entrypoint.sh", "/"]
RUN chmod u+x /entrypoint.sh
EXPOSE 53/udp
CMD ["/entrypoint.sh"]
