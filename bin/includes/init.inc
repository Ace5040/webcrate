writeLog "Initialization..."

writeLog "Creating var folders"
var_folders=(\
  "secrets"\
  "meta"\
  "meta/projects"\
  "dnsmasq"\
  "dnsmasq/hosts"\
  "crontabs"\
  "influxdb"\
  "influxdb/etc"\
  "influxdb/data"\
  "mysql-projects"\
  "mysql-services"\
  "mysql5-projects"\
  "postgresql-projects"\
  "mysql"\
  "mysql5"\
  "postgres"\
  "backup"\
  "backup-tmp"\
  "duplicity"\
  "ssh"\
  "openssl"\
  "letsencrypt"\
  "letsencrypt-meta"\
  "log"\
  "log/nginx"\
  "log/duplicity"\
  "log/graphana"\
  "nginx"\
  "nginx/confs"\
  "nginx/ssl"\
  "nginx/gzip"\
  "nginx/redirect"\
  "nginx/options"\
  "nginx/block"\
  "nginx/auth"\
  "phppgadmin"\
  "php_pools"\
  )
for i in "${var_folders[@]}"
do
  if [[ ! -d "./var/$i" ]]; then
    mkdir -p "./var/$i";
  fi
  # start_path=$(echo "$i" | cut -d/ -f1)
  chmod a-rw,u+rw ./var/$i
done
chmod -R a-rw,o+r,u+rw ./var/dnsmasq/hosts

MYSQL_ROOT_PASS=$(initDbFolder 'mysql')
MYSQL5_ROOT_PASS=$(initDbFolder 'mysql5')
POSTGRES_PASS=$(initDbFolder 'postgres')

GRAFANA_PASS=''
if [[ ! -d "./var/grafana/data" ]] ; then
  writeLog "Init grafana folders and generate password"
  mkdir -p "./var/grafana/data"
  mkdir -p "./var/grafana/log"
  if [[ ! -f "./var/secrets/grafana.secret" ]] ; then
    GRAFANA_PASS=`docker run --rm ace5040/webcrate-utils-pwgen:legacy /pwgen.sh`
    echo "user=admin" > ./var/secrets/grafana.secret
    echo "password=\"$GRAFANA_PASS\"" >> ./var/secrets/grafana.secret
  else
    GRAFANA_PASS=`grep 'password=' ./var/secrets/grafana.secret | sed -e 's/password=//' -e 's/^"//' -e 's/"$//'`
  fi
fi

if [[ ! -f "./var/secrets/admin.secret" ]] ; then
  writeLog "Generate webcrate secret and admin password"
  admin_password=`docker run --rm ace5040/webcrate-utils-pwgen:legacy /pwgen.sh`
  app_secret=`docker run --rm ace5040/webcrate-utils-pwgen:legacy pwgen -nAs1 32 1`
  echo "user=admin" > ./var/secrets/admin.secret
  echo "password=$admin_password" >> ./var/secrets/admin.secret
  echo "secret=$app_secret" >> ./var/secrets/admin.secret
fi

if [[ ! -f "./projects.yml" ]] ; then
  writeLog "Create default projects.yml"
  cp ./projects.yml.example ./projects.yml
fi
if [[ ! -f "./redirects.yml" ]] ; then
  writeLog "Create default redirects.yml"
  cp ./redirects.yml.example ./redirects.yml
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
