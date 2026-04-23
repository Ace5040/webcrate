source ./bin/includes/init.inc
uid=$(id -u);
gid=$(id -u);

writeLog "$(t "Generating resolv.conf for dnsmasq")" $LOG_LEVEL_DEBUG
rm -f ./var/dnsmasq/resolv.conf
touch ./var/dnsmasq/resolv.conf
if [ "$WEBCRATE_EXTERNAL_DNS_IP" != "" ]; then
	echo "nameserver $WEBCRATE_EXTERNAL_DNS_IP" >> ./var/dnsmasq/resolv.conf
else
	echo "nameserver 127.0.0.11" >> ./var/dnsmasq/resolv.conf
fi
writeLog "$(t "Generated resolv.conf for dnsmasq")" $LOG_LEVEL_DEBUG

writeLog "$(t "Parse projects started")" $LOG_LEVEL_INFO
docker run --rm --env-file=$(pwd)/.env --env-file=$(pwd)/images.default --entrypoint /parse-projects.py --name webcrate-docker-parse-projects \
	-e WEBCRATE_UID=$uid \
	-e WEBCRATE_GID=$gid \
	$PROJECTS_VOLUMES \
	-e WEBCRATE_PROJECTS_FOLDERS=$( IFS=:; printf '%s' "${WEBCRATE_PROJECTS_FOLDERS[*]}" ) \
	-e WEBCRATE_PWD=$(pwd) \
	-e LOG_LEVEL_VALUE=$LOG_LEVEL_VALUE \
	-v $(pwd)/projects.yml:/webcrate/projects.yml:ro \
	-v $(pwd)/var/log:/webcrate/log \
	-v $(pwd)/var/meta:/webcrate/meta \
	-v $(pwd)/var/crontabs:/webcrate/crontabs \
	-v $(pwd)/config/nginx-templates:/webcrate/nginx-templates:ro \
	-v $(pwd)/modules:/webcrate/modules:ro \
	-v $(pwd)/var/letsencrypt:/webcrate/letsencrypt:ro \
	-v $(pwd)/var/openssl:/webcrate/openssl:ro \
	-v $(pwd)/var/dnsmasq:/webcrate/dnsmasq \
	-v $(pwd)/var/nginx:/webcrate/nginx \
	-v $(pwd)/var/php_pools:/webcrate/php_pools \
	$IMAGE_UTILS_DOCKER
writeLog "$(t "Parse projects ended")" $LOG_LEVEL_INFO

writeLog "$(t "Parse redirects started")" $LOG_LEVEL_INFO
docker run --rm --env-file=$(pwd)/.env --entrypoint /parse-redirects.py --name webcrate-docker-parse-redirects \
	-e WEBCRATE_UID=$uid \
	-e WEBCRATE_GID=$gid \
	-e WEBCRATE_PWD=$(pwd) \
	-e LOG_LEVEL_VALUE=$LOG_LEVEL_VALUE \
	-v $(pwd)/redirects.yml:/webcrate/redirects.yml:ro \
	-v $(pwd)/var/log:/webcrate/log \
	-v $(pwd)/var/meta:/webcrate/meta \
	-v $(pwd)/config/nginx-templates:/webcrate/nginx-templates:ro \
	-v $(pwd)/var/letsencrypt:/webcrate/letsencrypt:ro \
	-v $(pwd)/var/openssl:/webcrate/openssl:ro \
	-v $(pwd)/var/dnsmasq:/webcrate/dnsmasq \
	-v $(pwd)/var/nginx:/webcrate/nginx \
	$IMAGE_UTILS_DOCKER
writeLog "$(t "Parse redirects ended")" $LOG_LEVEL_INFO

writeLog "$(t "Parse services started")" $LOG_LEVEL_INFO
docker run --rm --env-file=$(pwd)/.env --env-file=$(pwd)/images.default --entrypoint /parse-services.py --name webcrate-docker-parse-services \
	-e WEBCRATE_PWD=$(pwd) \
	-e LOG_LEVEL_VALUE=$LOG_LEVEL_VALUE \
	-v $(pwd)/services.yml:/webcrate/services.yml:ro \
	-v $(pwd)/config/nginx-templates:/webcrate/nginx-templates:ro \
	-v $(pwd)/var/letsencrypt:/webcrate/letsencrypt:ro \
	-v $(pwd)/var/openssl:/webcrate/openssl:ro \
	-v $(pwd)/var/log:/webcrate/log \
	-v $(pwd)/var/dnsmasq:/webcrate/dnsmasq \
	-v $(pwd)/var/nginx:/webcrate/nginx \
	$IMAGE_UTILS_DOCKER

writeLog "$(t "Parse services ended")" $LOG_LEVEL_INFO
