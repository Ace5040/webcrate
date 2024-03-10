SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
cd $SCRIPTPATH/..
source .env
source ./bin/includes/init.inc
uid=$(id -u);
gid=$(id -u);

if [ "$WEBCRATE_EXTERNAL_DNS_IP" != "" ]; then
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
docker run --rm --env-file=$(pwd)/.env --entrypoint /parse-projects.py --name webcrate-docker-parse-projects \
  -e WEBCRATE_UID=$uid \
  -e WEBCRATE_GID=$gid \
  $PROJECTS_VOLUMES \
  -e WEBCRATE_PROJECTS_FOLDERS=$( IFS=:; printf '%s' "${WEBCRATE_PROJECTS_FOLDERS[*]}" ) \
  -e WEBCRATE_PWD=$(pwd) \
  -v $(pwd)/projects.yml:/webcrate/projects.yml:ro \
  -v $(pwd)/var/log:/webcrate/log \
  -v $(pwd)/var/meta:/webcrate/meta \
  -v $(pwd)/var/crontabs:/webcrate/crontabs \
  -v $(pwd)/config/nginx-templates:/webcrate/nginx-templates:ro \
  -v $(pwd)/config/php-pool-templates:/webcrate/custom_templates:ro \
  -v $(pwd)/var/letsencrypt:/webcrate/letsencrypt:ro \
  -v $(pwd)/var/openssl:/webcrate/openssl:ro \
  -v $(pwd)/var/dnsmasq:/webcrate/dnsmasq \
  -v $(pwd)/var/nginx:/webcrate/nginx \
  -v $(pwd)/var/php_pools:/webcrate/php_pools \
  ace5040/webcrate-utils-docker:stable
writeLog "Parse projects ended"

writeLog "Parse redirects started"
docker run --rm --env-file=$(pwd)/.env --entrypoint /parse-redirects.py --name webcrate-docker-parse-redirects \
  -e WEBCRATE_UID=$uid \
  -e WEBCRATE_GID=$gid \
  -e WEBCRATE_PWD=$(pwd) \
  -v $(pwd)/redirects.yml:/webcrate/redirects.yml:ro \
  -v $(pwd)/var/log:/webcrate/log \
  -v $(pwd)/var/meta:/webcrate/meta \
  -v $(pwd)/config/nginx-templates:/webcrate/nginx-templates:ro \
  -v $(pwd)/var/letsencrypt:/webcrate/letsencrypt:ro \
  -v $(pwd)/var/openssl:/webcrate/openssl:ro \
  -v $(pwd)/var/dnsmasq:/webcrate/dnsmasq \
  -v $(pwd)/var/nginx:/webcrate/nginx \
  ace5040/webcrate-utils-docker:stable
writeLog "Parse redirects ended"

writeLog "Parse services started"
docker run --rm --env-file=$(pwd)/.env --entrypoint /parse-services.py --name webcrate-docker-parse-services \
  -e WEBCRATE_PWD=$(pwd) \
  -v $(pwd)/services.yml:/webcrate/services.yml:ro \
  -v $(pwd)/config/nginx-templates:/webcrate/nginx-templates:ro \
  -v $(pwd)/var/letsencrypt:/webcrate/letsencrypt:ro \
  -v $(pwd)/var/openssl:/webcrate/openssl:ro \
  -v $(pwd)/var/dnsmasq:/webcrate/dnsmasq \
  -v $(pwd)/var/nginx:/webcrate/nginx \
  ace5040/webcrate-utils-docker:stable

writeLog "Parse services ended"
