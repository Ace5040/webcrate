writeLog "Initialization..."

writeLog "Creating var folders"
var_folders=(\
  "secrets"\
  "meta/projects"\
  "dnsmasq/hosts"\
  "crontabs"\
  "influxdb"\
  "mysql"\
  "mysql5"\
  "postgres"\
  "backup"\
  "duplicity"\
  "ssh"\
  "openssl"\
  "letsencrypt"\
  "letsencrypt-meta"\
  "log/nginx"\
  "log/duplicity"\
  "log/graphana"\
  "nginx/projects"\
  "nginx/ssl"\
  "nginx/gzip"\
  "nginx/redirect"\
  "nginx/options"\
  "nginx/block"\
  "nginx/auth"\
  "phppgadmin"\
  "php_pools/php"\
  "php_pools/php56"\
  "php_pools/php73"\
  "php_pools/php74"\
  )
for i in "${var_folders[@]}"
do
  if [[ ! -d "./var/$i" ]] ; then mkdir -p "./var/$i"; fi
  chmod -R a-rw,u+rw ./var/$i
done
chmod a-rw,u+rw ./var/dnsmasq
chmod a-rw,o+r,u+rw ./var/dnsmasq/hosts

MYSQL_ROOT_PASS=$(initDbFolder 'mysql')
MYSQL5_ROOT_PASS=$(initDbFolder 'mysql5')
POSTGRES_PASS=$(initDbFolder 'postgres')

GRAFANA_PASS=''
if [[ ! -d "./var/grafana/data" ]] ; then
  writeLog "Init grafana folders and generate password"
  mkdir -p "./var/grafana/data"
  mkdir -p "./var/grafana/log"
  GRAFANA_PASS=`docker run --rm ace5040/webcrate-tools:stable /webcrate/pwgen.sh`
  echo "user=admin" > ./var/secrets/grafana.secret
  echo "password=\"$GRAFANA_PASS\"" >> ./var/secrets/grafana.secret
fi

if [[ ! -f "./var/secrets/webcrate.secret" ]] ; then
  writeLog "Generate webcrate secret and admin password"
  admin_password=`docker run --rm ace5040/webcrate-tools:stable /webcrate/pwgen.sh`
  app_secret=`docker run --rm ace5040/webcrate-tools:stable pwgen -nAs1 32 1`
  echo "user=admin" > ./var/secrets/webcrate.secret
  echo "password=$admin_password" >> ./var/secrets/webcrate.secret
  echo "secret=$app_secret" >> ./var/secrets/webcrate.secret
fi

if [[ ! -f "./projects.yml" ]] ; then
  writeLog "Create default projects.yml"
  cp ./projects.yml.example ./projects.yml
fi
if [[ ! -f "./services.yml" ]] ; then
  writeLog "Create default services.yml"
  cp ./services.yml.example ./services.yml
fi

writeLog "Create docker network if it not exists"
if docker network inspect webcrate_network >/dev/null 2> /dev/null; then
  echo network webcrate_network exists
else
  docker network create --driver=bridge --subnet=10.255.0.0/24 webcrate_network > /dev/null
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
