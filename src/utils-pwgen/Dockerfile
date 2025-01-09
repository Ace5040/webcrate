ARG IMAGE_ALPINE_BASE
FROM $IMAGE_ALPINE_BASE
COPY pwgen.sh /pwgen.sh
RUN apk update &&\
    apk add pwgen &&\
    rm -rf /var/cache/apk/* &&\
    chmod u+x /pwgen.sh
