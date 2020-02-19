FROM nginx:stable
RUN mkdir -p /sitesbox
COPY generate_configs.sh /sitesbox/generate_configs.sh
RUN chmod u+x /sitesbox/generate_configs.sh
COPY entrypoint.sh /entrypoint.sh
RUN chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
