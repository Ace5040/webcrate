FROM alpine:latest

RUN apk update
RUN apk add --no-cache dnsmasq-dnssec

COPY ["entrypoint.sh", "/"]
RUN chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
