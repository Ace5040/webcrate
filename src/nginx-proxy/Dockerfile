FROM nginx:stable
RUN apt-get update
RUN apt-get --assume-yes install python3 python3-pip
RUN pip3 install pyyaml munch
RUN mkdir -p /webcrate
COPY parse-users.py /webcrate/parse-users.py
RUN chmod u+x /webcrate/parse-users.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
