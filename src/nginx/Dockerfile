FROM nginx:stable
RUN apt-get update
RUN apt-get --assume-yes install python3 python3-pip sudo
RUN pip3 install pyyaml munch
RUN mkdir -p /webcrate
COPY parse-projects.py /webcrate/parse-projects.py
COPY reload.py /webcrate/reload.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod u+x /webcrate/parse-projects.py; \
    chmod u+x /webcrate/reload.py; \
    chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
