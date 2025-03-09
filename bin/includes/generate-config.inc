source ./bin/includes/init.inc
uid=$(id -u);
gid=$(id -u);

if [ "$WEBCRATE_EXTERNAL_DNS_IP" != "" ]; then
	writeLog "Generating resolv.conf for dnsmasq" $LOG_LEVEL_DEBUG
	rm -f ./var/dnsmasq/resolv.conf
	touch ./var/dnsmasq/resolv.conf
	echo "nameserver $WEBCRATE_EXTERNAL_DNS_IP" >> ./var/dnsmasq/resolv.conf
	writeLog "Generated resolv.conf for dnsmasq" $LOG_LEVEL_DEBUG
fi

writeLog "Parse projects started" $LOG_LEVEL_INFO
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
	-v $(pwd)/config/php-pool-templates:/webcrate/custom_templates:ro \
	-v $(pwd)/var/letsencrypt:/webcrate/letsencrypt:ro \
	-v $(pwd)/var/openssl:/webcrate/openssl:ro \
	-v $(pwd)/var/dnsmasq:/webcrate/dnsmasq \
	-v $(pwd)/var/nginx:/webcrate/nginx \
	-v $(pwd)/var/php_pools:/webcrate/php_pools \
	$IMAGE_UTILS_DOCKER
writeLog "Parse projects ended" $LOG_LEVEL_INFO

writeLog "Parse redirects started" $LOG_LEVEL_INFO
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
writeLog "Parse redirects ended" $LOG_LEVEL_INFO

writeLog "Parse services started" $LOG_LEVEL_INFO
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

writeLog "Parse services ended" $LOG_LEVEL_INFO
