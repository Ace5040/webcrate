source ./bin/wc-functions.inc

MYSQL_ROOT_PASS=$(initDbFolder 'mysql')
MYSQL5_ROOT_PASS=$(initDbFolder 'mysql5')
POSTGRES_PASS=$(initDbFolder 'postgres')

if [[ ! -f "./users.yml" ]] ; then
  cp ./users.yml.example ./users.yml
fi
if [[ ! -f "./services.yml" ]] ; then
  cp ./services.yml.example ./services.yml
fi

var_folders=( "meta" "mysql" "synapse" "ssh" "mysql5" "postgres" "sites" "duplicity" "letsencrypt" "letsencrypt-meta/well-known" "openssl" "crontabs" "backup" "secrets" "solr/cores" "solr/logs" "influxdb" "logs/nginx" )
for i in "${var_folders[@]}"
do
  if [[ ! -d "./var/$i" ]] ; then mkdir -p "./var/$i"; fi
done

GRAFANA_PASS=''
if [[ ! -d "./var/grafana/data" ]] ; then
  mkdir -p "./var/grafana/data"
  mkdir -p "./var/grafana/log"
  GRAFANA_PASS=`docker run --rm ace5040/webcrate-utils:stable /webcrate/pwgen.sh`
  echo "user=admin" > ./var/secrets/grafana.secret
  echo "password=\"$GRAFANA_PASS\"" >> ./var/secrets/grafana.secret
fi

if [[ ! -f "./var/secrets/webcrate.secret" ]] ; then
  admin_password=`docker run --rm ace5040/webcrate-utils:stable /webcrate/pwgen.sh`
  app_secret=`docker run --rm ace5040/webcrate-utils:stable pwgen -nAs1 32 1`
  echo "user=admin" > ./var/secrets/webcrate.secret
  echo "password=$admin_password" >> ./var/secrets/webcrate.secret
  echo "secret=$app_secret" >> ./var/secrets/webcrate.secret
fi

SYNAPSE_PASS=''
if [[ ! -f "./var/secrets/synapse.secret" ]] ; then
  SYNAPSE_PASS=`docker run --rm ace5040/webcrate-utils:stable /webcrate/pwgen.sh`
  TURN_SHARED_SECRET=`docker run --rm ace5040/webcrate-utils:stable pwgen -nAs1 32 1`
  echo "user=admin" > ./var/secrets/synapse.secret
  echo "password=$SYNAPSE_PASS" >> ./var/secrets/synapse.secret
  echo $TURN_SHARED_SECRET >> ./var/secrets/turn.secret
fi
WEBCRATE_SYNAPSE_DOMAIN=`cat ./services.yml | awk "/synapse:/,/port:/" | grep -oP "(?<=domain: ).*" | head -c -1`

volumes=( webcrate_dnsmasq_hosts webcrate_nginx_configs webcrate_ssl_configs webcrate_redirect_configs webcrate_options_configs webcrate_block_configs webcrate_auth_locations_configs webcrate_gzip_configs webcrate_php56_pools webcrate_php73_pools webcrate_php74_pools webcrate_php80_pools webcrate_phpmyadmin webcrate_phpmyadmin_config webcrate_phpmyadmin_sessions webcrate_phppgadmin webcrate_phppgadmin_logs webcrate_coturn )
for i in "${volumes[@]}"
do
	if docker volume inspect $i >/dev/null 2> /dev/null; then
    echo volume $i exists
  else
    docker volume create $i >/dev/null
  fi
done
if docker network inspect webcrate_network >/dev/null 2> /dev/null; then
  echo network webcrate_network exists
else
  docker network create --driver=bridge --subnet=172.31.0.0/16 webcrate_network > /dev/null
fi
