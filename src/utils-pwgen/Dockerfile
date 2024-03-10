FROM alpine:3
COPY pwgen.sh /pwgen.sh
RUN apk update &&\
    apk add pwgen &&\
    rm -rf /var/cache/apk/* &&\
    chmod u+x /pwgen.sh
