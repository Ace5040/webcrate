source ./bin/wc-functions.inc

MYSQL_ROOT_PASS=$(initDbFolder 'mysql')
MYSQL5_ROOT_PASS=$(initDbFolder 'mysql5')
POSTGRES_PASS=$(initDbFolder 'postgres')

if [[ ! -f "./projects.yml" ]] ; then
  cp ./projects.yml.example ./projects.yml
fi
if [[ ! -f "./services.yml" ]] ; then
  cp ./services.yml.example ./services.yml
fi

PROJECTS_VOLUMES=""
VOLUMES_COUNTER=0
for SITES_PATH in ${WEBCRATE_PROJECTS_FOLDERS[@]}
do
    if [[ $SITES_PATH == /* ]]; then
      SITES_ABSOLUTE_PATH=$SITES_PATH;
    else
      SITES_ABSOLUTE_PATH=$(pwd)/$SITES_PATH;
    fi
    if [[ $VOLUMES_COUNTER != 0 ]]; then let VOLUME_INDEX=$VOLUMES_COUNTER+1; else VOLUME_INDEX=""; fi
    if [[ ! -d "$SITES_ABSOLUTE_PATH" ]] ; then mkdir -p "$SITES_ABSOLUTE_PATH"; fi
    PROJECTS_VOLUMES="$PROJECTS_VOLUMES-v $SITES_ABSOLUTE_PATH:/projects${VOLUME_INDEX} "
    let VOLUMES_COUNTER+=1
done

var_folders=( "meta" "mysql" "synapse" "ssh" "mysql5" "postgres" "duplicity" "letsencrypt" "letsencrypt-meta/well-known" "openssl" "crontabs" "backup" "secrets" "solr/cores" "solr/logs" "influxdb" "logs/nginx" )
for i in "${var_folders[@]}"
do
  if [[ ! -d "./var/$i" ]] ; then mkdir -p "./var/$i"; fi
  chmod -R a-rw,u+rw ./var/$i
done
chmod -R a+r ./var/meta

GRAFANA_PASS=''
if [[ ! -d "./var/grafana/data" ]] ; then
  mkdir -p "./var/grafana/data"
  mkdir -p "./var/grafana/log"
  GRAFANA_PASS=`docker run --rm ace5040/webcrate-tools:stable /webcrate/pwgen.sh`
  echo "user=admin" > ./var/secrets/grafana.secret
  echo "password=\"$GRAFANA_PASS\"" >> ./var/secrets/grafana.secret
fi

if [[ ! -f "./var/secrets/webcrate.secret" ]] ; then
  admin_password=`docker run --rm ace5040/webcrate-tools:stable /webcrate/pwgen.sh`
  app_secret=`docker run --rm ace5040/webcrate-tools:stable pwgen -nAs1 32 1`
  echo "user=admin" > ./var/secrets/webcrate.secret
  echo "password=$admin_password" >> ./var/secrets/webcrate.secret
  echo "secret=$app_secret" >> ./var/secrets/webcrate.secret
fi

SYNAPSE_PASS=''
if [[ ! -f "./var/secrets/synapse.secret" ]] ; then
  SYNAPSE_PASS=`docker run --rm ace5040/webcrate-tools:stable /webcrate/pwgen.sh`
  TURN_SHARED_SECRET=`docker run --rm ace5040/webcrate-tools:stable pwgen -nAs1 32 1`
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
