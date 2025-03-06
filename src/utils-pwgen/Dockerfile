ARG IMAGE
FROM $IMAGE
COPY pwgen.sh /pwgen.sh
RUN apk update &&\
    apk add pwgen &&\
    rm -rf /var/cache/apk/* &&\
    chmod u+x /pwgen.sh
