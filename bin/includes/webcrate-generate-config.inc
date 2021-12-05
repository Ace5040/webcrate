SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
cd $SCRIPTPATH/..
source .env
source ./bin/includes/webcrate-init.inc
uid=$(id -u);
gid=$(id -u);

if [ "$WEBCRATE_MODE" == "DEV" ] && [ "$WEBCRATE_EXTERNAL_DNS_IP" != "" ]; then
  writeLog "Generate resolv.conf for dnsmasq"
  rm -f ./var/dnsmasq/resolv.conf
  touch ./var/dnsmasq/resolv.conf
  for IP_ADDR in ${WEBCRATE_SECONDARY_INSTANCES[@]}
  do
    echo "nameserver $IP_ADDR" >> ./var/dnsmasq/resolv.conf
  done
  echo "nameserver $WEBCRATE_EXTERNAL_DNS_IP" >> ./var/dnsmasq/resolv.conf
fi

writeLog "Parse projects started"
docker run --rm --env-file=$(pwd)/.env --entrypoint /webcrate/parse-projects.py \
  -e WEBCRATE_UID=$uid \
  -e WEBCRATE_GID=$gid \
  $PROJECTS_VOLUMES \
  -v $(pwd)/projects.yml:/webcrate/projects.yml:ro \
  -v $(pwd)/var/meta:/webcrate/meta \
  -v $(pwd)/config/nginx-templates:/webcrate/nginx-templates:ro \
  -v $(pwd)/config/php-pool-templates:/webcrate/custom_templates:ro \
  -v $(pwd)/var/letsencrypt:/webcrate/letsencrypt:ro \
  -v $(pwd)/var/openssl:/webcrate/openssl:ro \
  -v webcrate_nginx_configs:/webcrate/nginx_configs \
  -v webcrate_ssl_configs:/webcrate/ssl_configs \
  -v webcrate_gzip_configs:/webcrate/gzip_configs \
  -v webcrate_redirect_configs:/webcrate/redirect_configs \
  -v webcrate_options_configs:/webcrate/options_configs \
  -v webcrate_block_configs:/webcrate/block_configs \
  -v webcrate_auth_locations_configs:/webcrate/auth_locations_configs \
  -v webcrate_php56_pools:/webcrate/php56-fpm.d \
  -v webcrate_php73_pools:/webcrate/php73-fpm.d \
  -v webcrate_php74_pools:/webcrate/php74-fpm.d \
  -v webcrate_php_pools:/webcrate/php-fpm.d \
  -v webcrate_dnsmasq_hosts:/webcrate-dnsmasq/config \
  ace5040/webcrate-tools:stable

writeLog "Parse projects ended"
writeLog "Parse services started"

docker run --rm --env-file=$(pwd)/.env --entrypoint /webcrate/parse-services.py \
  -v $(pwd)/services.yml:/webcrate/services.yml:ro \
  -v $(pwd)/config/nginx-templates:/webcrate/nginx-templates:ro \
  -v $(pwd)/var/letsencrypt:/webcrate/letsencrypt:ro \
  -v $(pwd)/var/openssl:/webcrate/openssl:ro \
  -v webcrate_nginx_configs:/webcrate/nginx_configs \
  -v webcrate_ssl_configs:/webcrate/ssl_configs \
  -v webcrate_dnsmasq_hosts:/webcrate-dnsmasq/config \
  ace5040/webcrate-tools:stable

writeLog "Parse services ended"