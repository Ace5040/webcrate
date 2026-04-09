ARG IMAGE
FROM $IMAGE
COPY pwgen.sh /pwgen.sh
RUN apk add --no-cache pwgen && \
    chmod u+x /pwgen.sh
