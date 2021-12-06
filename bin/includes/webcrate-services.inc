backends=( "gunicorn" "php56" "php73" "php74" "php" )
PROJECT_COUNT=1
PROJECTS_LIST=()
for backend in "${backends[@]}"
do
  if [ -f ./var/meta/projects-$backend.list ]; then
    while read -r line; do
      project=($line)
      project_name=${project[0]}
      image_name=${project[1]}
      container_name=${project[2]}
      ssh_port=${project[3]}
      project_domain=${project[4]}

      PROJECT_VOLUME=""
      PROJECTS_LIST+=("${project_name}")
      for SITES_PATH in ${WEBCRATE_PROJECTS_FOLDERS[@]}
      do
        if [[ $SITES_PATH == /* ]]; then
          SITES_ABSOLUTE_PATH=$SITES_PATH;
        else
          SITES_ABSOLUTE_PATH=$(pwd)/$SITES_PATH;
        fi
        if [ ! -d "$SITES_ABSOLUTE_PATH" ] ; then mkdir -p "$SITES_ABSOLUTE_PATH"; fi
        if [ -d "$SITES_ABSOLUTE_PATH/$project_name" ]; then
          PROJECT_VOLUME="-v $SITES_ABSOLUTE_PATH/$project_name:/home/$project_name"
          break
        fi
      done

      PHP_CONFIGS=""
      PHP_POOL_TEMPLATES=""
      if [ $backend == 'php56' ] || [ $backend == 'php73' ] || [ $backend == 'php74' ] || [ $backend == 'php' ]; then
        PHP_POOL_TEMPLATES="-v $(pwd)/config/php-pool-templates:/webcrate/custom_templates:ro"
        PHP_CONFIGS="-v $(pwd)/config/php/$backend.ini:/etc/$backend/conf.d/user.ini:ro -v webcrate_${backend}_pools:/webcrate/pools"
      fi

      writeLog "Create docker network for ${project_name} if it not exists"
      if docker network inspect webcrate_network_${project_name} >/dev/null 2> /dev/null; then
        echo network webcrate_network_${project_name} exists
      else
        docker network create --driver=bridge --subnet=10.$PROJECT_COUNT.0.0/24 webcrate_network_${project_name} > /dev/null
      fi
      writeLog "Starting $container_name container for $project_name"
      if docker container inspect $container_name >/dev/null 2> /dev/null; then
        writeLog "service $container_name exists"
      else
        docker run -d --env-file=$(pwd)/.env --hostname $container_name --name $container_name \
          --network="webcrate_network_${project_name}" --dns=10.$PROJECT_COUNT.0.250 \
          --restart="unless-stopped" \
          -p "$ssh_port:22" \
          -e WEBCRATE_UID=$uid \
          -e WEBCRATE_GID=$gid \
          -e WEBCRATE_PROJECT=$project_name \
          -e WEBCRATE_DOMAIN=$project_domain \
          -v /etc/localtime:/etc/localtime:ro \
          $PROJECT_VOLUME \
          -v $(pwd)/var/crontabs:/var/spool/cron \
          -v $(pwd)/config/telegraf:/etc/telegraf/telegraf.d:ro \
          -v $(pwd)/projects.yml:/webcrate/projects.yml:ro \
          -v $(pwd)/var/ssh:/webcrate/ssh_keys \
          -v $(pwd)/var/meta:/webcrate/meta \
          -v $(pwd)/config/exim/exim.conf:/etc/mail/exim.original.conf \
          $PHP_POOL_TEMPLATES \
          $PHP_CONFIGS \
          ace5040/$image_name:stable > /dev/null
      fi
      let PROJECT_COUNT+=1
    done < "./var/meta/projects-$backend.list"
  fi
done

writeLog "Starting webcrate-dnsmasq container"
if docker container inspect webcrate-dnsmasq >/dev/null 2> /dev/null; then
  writeLog "service webcrate-dnsmasq exists"
else
  DNSPORT=""
  if [ "$WEBCRATE_LOCALDNS" = true ]; then
    DNSPORT=-p\ "53:53/udp"
  fi
  docker create --hostname webcrate-dnsmasq --name webcrate-dnsmasq \
    --network="webcrate_network" --ip=10.255.0.100 \
    --restart="unless-stopped" \
    $DNSPORT \
    -v $(pwd)/var/dnsmasq:/dnsmasq \
    -v webcrate_dnsmasq_hosts:/dnsmasq-hosts \
    ace5040/webcrate-dnsmasq:stable > /dev/null
  PROJECT_COUNT=1
  for project_name in "${PROJECTS_LIST[@]}"
  do
    docker network connect --ip=10.$PROJECT_COUNT.0.250 webcrate_network_$project_name webcrate-dnsmasq
    let PROJECT_COUNT+=1
  done
  docker start webcrate-dnsmasq
fi

writeLog "Starting webcrate-admin container"

if docker container inspect webcrate >/dev/null 2> /dev/null; then
  writeLog "service webcrate exists"
else
  if [ "$WEBCRATE_APP_MODE" == "DEV" ]; then WEBCRATE_APP_SRC=-v\ $(pwd)/src/webcrate-admin/app:/app; else WEBCRATE_APP_SRC=""; fi
  docker run -d --env-file=$(pwd)/.env --hostname webcrate --name webcrate \
    --network="webcrate_network" --dns=10.255.0.100 \
    --restart="unless-stopped" \
    -e WEBCRATE_UID=$uid \
    -e WEBCRATE_GID=$gid \
    -e WEBCRATE_PROJECTS_FOLDERS=$( IFS=:; printf '%s' "${WEBCRATE_PROJECTS_FOLDERS[*]}" ) \
    -v /etc/localtime:/etc/localtime:ro \
    -v $DOCKER_SOCKET:/var/run/docker.sock \
    $WEBCRATE_APP_SRC \
    -v $(pwd)/var/meta:/webcrate/meta \
    -v $(pwd)/var/secrets:/webcrate/secrets \
    -v $(pwd)/projects.yml:/webcrate/projects.yml \
    -v $(pwd)/services.yml:/webcrate/services.yml \
    ace5040/webcrate-admin:stable > /dev/null
fi

writeLog "Starting memcached container"

if [ "$WEBCRATE_SERVICE_MEMCACHED" = true ]; then
  if docker container inspect memcached >/dev/null 2> /dev/null; then
    writeLog "service memcached exists"
  else
    docker create --env-file=$(pwd)/.env --log-driver=none --name memcached \
      --network="webcrate_network" --dns=10.255.0.100 \
      --restart="unless-stopped" \
      memcached:1 > /dev/null
    for project_name in "${PROJECTS_LIST[@]}"
    do
      docker network connect webcrate_network_$project_name memcached
    done
    docker start memcached
  fi
fi

writeLog "Starting mysql5 container"

if docker container inspect mysql5 >/dev/null 2> /dev/null; then
  writeLog "service mysql5 exists"
else
  if [ "$MYSQL5_ROOT_PASS" != "" ]; then MYSQL5_ROOT_PASS=-e\ MYSQL_ROOT_PASSWORD="$MYSQL5_ROOT_PASS"; fi
  docker create --env-file=$(pwd)/.env --name mysql5 \
    --network="webcrate_network" --dns=10.255.0.100 \
    --restart="unless-stopped" \
    --user "$uid:$gid" \
    $MYSQL5_ROOT_PASS \
    -v /etc/localtime:/etc/localtime:ro \
    -v $(pwd)/var/mysql5:/var/lib/mysql \
    -v $(pwd)/config/mysql/mysql5.cnf:/etc/mysql/conf.d/user.cnf \
    mariadb:5 > /dev/null
  for project_name in "${PROJECTS_LIST[@]}"
  do
    docker network connect webcrate_network_$project_name mysql5
  done
  docker start mysql5
fi

writeLog "Starting mysql container"

if docker container inspect mysql >/dev/null 2> /dev/null; then
  writeLog "service mysql exists"
else
  if [ "$MYSQL_ROOT_PASS" != "" ]; then MYSQL_ROOT_PASS=-e\ MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASS"; fi
  docker create --env-file=$(pwd)/.env --name mysql \
    --network="webcrate_network" --dns=10.255.0.100 \
    --restart="unless-stopped" \
    --user "$uid:$gid" \
    $MYSQL_ROOT_PASS \
    -v /etc/localtime:/etc/localtime:ro \
    -v $(pwd)/var/mysql:/var/lib/mysql \
    -v $(pwd)/config/mysql/mysql.cnf:/etc/mysql/conf.d/user.cnf \
    mariadb:10 > /dev/null
  for project_name in "${PROJECTS_LIST[@]}"
  do
    docker network connect webcrate_network_$project_name mysql
  done
  docker start mysql
fi

writeLog "Starting postgres container"

if docker container inspect postgres >/dev/null 2> /dev/null; then
  writeLog "service postgres exists"
else
  if [ "$POSTGRES_PASS" != "" ]; then POSTGRES_PASS=-e\ POSTGRES_PASSWORD="$POSTGRES_PASS"; fi
  docker create --env-file=$(pwd)/.env --name postgres \
    --network="webcrate_network" --dns=10.255.0.100 \
    --restart="unless-stopped" \
    --user "$uid:$gid" \
    $POSTGRES_PASS \
    -v $(pwd)/var/postgres:/var/lib/postgresql/data \
    postgres:12 > /dev/null
  for project_name in "${PROJECTS_LIST[@]}"
  do
    docker network connect webcrate_network_$project_name postgres
  done
  docker start postgres
fi

writeLog "Starting phpmyadmin container"

if docker container inspect phpmyadmin >/dev/null 2> /dev/null; then
  writeLog "service phpmyadmin exists"
else
  docker run -d --env-file=$(pwd)/.env --name phpmyadmin \
    --network="webcrate_network" --dns=10.255.0.100 \
    --restart="unless-stopped" \
    -e PMA_HOSTS=mysql,mysql5 \
    -e UPLOAD_LIMIT=2048M \
    -v /etc/localtime:/etc/localtime:ro \
    -v $(pwd)/config/phpmyadmin/php.ini:/usr/local/etc/php/php.ini:ro \
    -v $(pwd)/config/phpmyadmin/config.user.inc.php:/etc/phpmyadmin/config.user.inc.php:ro \
    -v webcrate_phpmyadmin_sessions:/sessions \
    -v webcrate_phpmyadmin:/var/www/html \
    -v webcrate_phpmyadmin_config:/etc/phpmyadmin \
    phpmyadmin/phpmyadmin:5 > /dev/null
fi

writeLog "Starting phppgadmin container"

if docker container inspect phppgadmin >/dev/null 2> /dev/null; then
  writeLog "service phppgadmin exists"
else
  docker run -d --env-file=$(pwd)/.env --name phppgadmin \
    --network="webcrate_network" --dns=10.255.0.100 \
    --restart="unless-stopped" \
    -e DATABASE_HOST=postgres \
    -v /etc/localtime:/etc/localtime:ro \
    -v webcrate_phppgadmin:/bitnami \
    bitnami/phppgadmin:7 > /dev/null
fi

if [ "$WEBCRATE_SERVICE_DOCTOHTML" = true ]; then
  writeLog "Starting doctohtml container"
  if docker container inspect doctohtml >/dev/null 2> /dev/null; then
    writeLog "service doctohtml exists"
  else
    docker create --env-file=$(pwd)/.env --name doctohtml \
      --network="webcrate_network" --dns=10.255.0.100 \
      --restart="unless-stopped" \
      -p "3000:3000" \
      ace5040/doctohtml:stable > /dev/null
    for project_name in "${PROJECTS_LIST[@]}"
    do
      docker network connect webcrate_network_$project_name doctohtml
    done
    docker start doctohtml
  fi
fi

if [ "$WEBCRATE_SERVICE_HTMLTOPDF" = true ]; then
  writeLog "Starting htmltopdf container"
  if docker container inspect htmltopdf >/dev/null 2> /dev/null; then
    writeLog "service htmltopdf exists"
  else
    docker create --env-file=$(pwd)/.env --name htmltopdf \
      --network="webcrate_network" --dns=10.255.0.100 \
      --restart="unless-stopped" \
      -p "3001:3000" \
      ace5040/htmltopdf:latest > /dev/null
    for project_name in "${PROJECTS_LIST[@]}"
    do
      docker network connect webcrate_network_$project_name htmltopdf
    done
    docker start htmltopdf
  fi
fi

if [ "$WEBCRATE_SERVICE_SOLR" = true ]; then
  writeLog "Starting solr container"
  if docker container inspect solr >/dev/null 2> /dev/null; then
    writeLog "service solr exists"
  else
    docker create --env-file=$(pwd)/.env --log-driver=none --name solr \
      --network="webcrate_network" \
      --restart="unless-stopped" \
      --user "$uid:$gid" \
      -p "8983:8983" \
      -v /etc/localtime:/etc/localtime:ro \
      -v $(pwd)/var/solr/logs:/opt/solr/server/logs \
      -v $(pwd)/var/solr/cores:/opt/solr/server/solr/mycores \
      --entrypoint docker-entrypoint.sh \
      solr:6 solr -m 4096m -force -f > /dev/null
    for project_name in "${PROJECTS_LIST[@]}"
    do
      docker network connect webcrate_network_$project_name solr
    done
    docker start solr
  fi
fi

if [ "$WEBCRATE_SERVICE_STATS" = true ]; then
  writeLog "Starting graphana and influxdb containers"
  if docker container inspect grafana >/dev/null 2> /dev/null; then
    writeLog "service grafana exists"
  else
    docker run -d --env-file=$(pwd)/.env --log-driver=none --name grafana \
      --network="webcrate_network" --dns=10.255.0.100 \
      --restart="unless-stopped" \
      --user "$uid:$gid" \
      -e GF_PATHS_DATA=/data \
      -e GF_PATHS_LOGS=/log \
      -e GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/home.json \
      -v /etc/localtime:/etc/localtime:ro \
      -v $(pwd)/var/grafana/data:/data \
      -v $(pwd)/var/grafana/log:/log \
      -v $(pwd)/config/grafana/home.json:/home.json \
      -v $(pwd)/config/grafana/dashboard.yml:/etc/grafana/provisioning/dashboards/default.yml \
      -v $(pwd)/config/grafana/datasource.yml:/etc/grafana/provisioning/datasources/default.yml \
      grafana/grafana:7.4.3 > /dev/null
  fi
  if docker container inspect influxdb >/dev/null 2> /dev/null; then
    writeLog "service influxdb exists"
  else
    docker create --env-file=$(pwd)/.env --log-driver=none --name influxdb \
      --network="webcrate_network" --dns=10.255.0.100 \
      --restart="unless-stopped" \
      --user "$uid:$gid" \
      -e INFLUXDB_DB=telegraf \
      -v /etc/localtime:/etc/localtime:ro \
      -v $(pwd)/var/influxdb:/var/lib/influxdb \
      influxdb:1.8-alpine > /dev/null
    for project_name in "${PROJECTS_LIST[@]}"
    do
      docker network connect webcrate_network_$project_name influxdb
    done
    docker start influxdb
  fi
  if [ "$GRAFANA_PASS" != "" ]; then
    sleep 10; docker exec --user $uid:$gid grafana grafana-cli admin reset-admin-password "$GRAFANA_PASS"
  fi
fi

if [ "$WEBCRATE_SERVICE_SYNAPSE" = true ]; then
  writeLog "Starting synapse, synapse-admin and turn containers"
  if docker container inspect synapse >/dev/null 2> /dev/null; then
    writeLog "service synapse exists"
  else
    turn_secret=`cat ./var/secrets/turn.secret`

    if [[ ! -f "./var/synapse/homeserver.yaml" ]] ; then
      docker run -it --rm --hostname synapse --name synapse \
        --user "$uid:$gid" \
        --network="webcrate_network" --dns=10.255.0.100 \
        -v $(pwd)/var/synapse:/data \
        -e SYNAPSE_SERVER_NAME=$WEBCRATE_SYNAPSE_DOMAIN \
        -e UID=$uid \
        -e GID=$gid \
        -e SYNAPSE_REPORT_STATS=yes \
        matrixdotorg/synapse:latest generate
      echo "" >> ./var/synapse/homeserver.yaml
      echo "turn_uris:" >> ./var/synapse/homeserver.yaml
      echo "  - \"turns:$WEBCRATE_SYNAPSE_DOMAIN?transport=udp\"" >> ./var/synapse/homeserver.yaml
      echo "  - \"turns:$WEBCRATE_SYNAPSE_DOMAIN?transport=udp\"" >> ./var/synapse/homeserver.yaml
      echo "  - \"turn:$WEBCRATE_SYNAPSE_DOMAIN?transport=udp\"" >> ./var/synapse/homeserver.yaml
      echo "  - \"turn:$WEBCRATE_SYNAPSE_DOMAIN?transport=udp\"" >> ./var/synapse/homeserver.yaml
      echo "turn_user_lifetime: \"10h\"" >> ./var/synapse/homeserver.yaml
      echo "turn_shared_secret: \"$turn_secret\"" >> ./var/synapse/homeserver.yaml
      echo "suppress_key_server_warning: true" >> ./var/synapse/homeserver.yaml

      sed -i "s/^#max_upload_size: 10M$/max_upload_size: 10M/g" ./var/synapse/homeserver.yaml;
      sed -i "s/^database:$/#database:/g" ./var/synapse/homeserver.yaml;
      sed -i "s/^  name: sqlite3$/#  name: sqlite3/g" ./var/synapse/homeserver.yaml;
      sed -i "s/^  args:$/#  args:/g" ./var/synapse/homeserver.yaml;
      sed -i "s/^    database: \/data\/homeserver.db$/#    database: \/data\/homeserver.db/g" ./var/synapse/homeserver.yaml;

      SYNAPSE_POSTGRES_PASS='';
      if [[ -f "./var/secrets/synapse-service-postgres.txt" ]] ; then
        SYNAPSE_POSTGRES_PASS=`cat ./var/secrets/synapse-service-postgres.txt|grep 'password='|grep -oP "(?<=password=).*" | head -c -1`
      fi

      echo "" >> ./var/synapse/homeserver.yaml
      echo "database:" >> ./var/synapse/homeserver.yaml
      echo "  name: psycopg2" >> ./var/synapse/homeserver.yaml
      echo "  args:" >> ./var/synapse/homeserver.yaml
      echo "    user: synapse" >> ./var/synapse/homeserver.yaml
      echo "    password: \"$SYNAPSE_POSTGRES_PASS\"" >> ./var/synapse/homeserver.yaml
      echo "    database: synapse" >> ./var/synapse/homeserver.yaml
      echo "    host: postgres" >> ./var/synapse/homeserver.yaml
      echo "    cp_min: 5" >> ./var/synapse/homeserver.yaml
      echo "    cp_max: 10" >> ./var/synapse/homeserver.yaml

      echo "" >> ./var/synapse/homeserver.yaml
      echo "user_directory:" >> ./var/synapse/homeserver.yaml
      echo "  search_all_projects: true" >> ./var/synapse/homeserver.yaml

    fi

    docker run -d --hostname synapse --name synapse \
      --network="webcrate_network" --dns=10.255.0.100 \
      --restart="unless-stopped" \
      --user "$uid:$gid" \
      -e UID=$uid \
      -e GID=$gid \
      -v $(pwd)/var/synapse:/data \
      -v $(pwd)/var/openssl:/webcrate/openssl \
      matrixdotorg/synapse:latest
  fi

  if docker container inspect turn >/dev/null 2> /dev/null; then
    writeLog "service turn exists"
  else
    docker run -d --hostname turn --name turn \
      --network="webcrate_network" --dns=10.255.0.100 \
      --restart="unless-stopped" \
      -v $(pwd)/config/turn:/webcrate \
      -v webcrate_coturn:/var/lib/coturn \
      -p "3478:3478/udp" \
      -p "3479:3479/udp" \
      -p "5349:5349/udp" \
      -p "49160-49200:49160-49200/udp" \
      instrumentisto/coturn:4 -c /webcrate/turn.conf  \
        --realm $WEBCRATE_SYNAPSE_DOMAIN \
        --static-auth-secret="$turn_secret" \
        --external-ip='$(detect-external-ip)' \
        --relay-ip='$(detect-external-ip)'
  fi

  if docker container inspect synapse-admin >/dev/null 2> /dev/null; then
    writeLog "service synapse-admin exists"
  else
    docker run -d --env-file=$(pwd)/.env --hostname synapse-admin --name synapse-admin \
      --network="webcrate_network" --dns=10.255.0.100 \
      --restart="unless-stopped" \
      awesometechnologies/synapse-admin:latest
  fi

  if [ "$SYNAPSE_PASS" != "" ]; then
    sleep 10; docker exec synapse register_new_matrix_user -a --user admin --password "$SYNAPSE_PASS" -c /data/homeserver.yaml http://localhost:8008
  fi

fi

writeLog "Starting nginx container"
if docker container inspect webcrate-nginx >/dev/null 2> /dev/null; then
   writeLog "service webcrate-nginx exists"
else

  PROJECTS_HOMES=""
  for SITES_PATH in ${WEBCRATE_PROJECTS_FOLDERS[@]}
  do
    if [[ $SITES_PATH == /* ]]; then
      SITES_ABSOLUTE_PATH=$SITES_PATH;
    else
      SITES_ABSOLUTE_PATH=$(pwd)/$SITES_PATH;
    fi
    for dir in $(find $SITES_ABSOLUTE_PATH -mindepth 1 -maxdepth 1 -type d); do
      project_name=`basename $dir`
      PROJECTS_HOMES="$PROJECTS_HOMES-v $SITES_ABSOLUTE_PATH/$project_name:/home/$project_name "
    done
  done

  docker create --env-file=$(pwd)/.env --hostname webcrate-nginx --name webcrate-nginx \
    --network="webcrate_network" \
    -p "80:1080" \
    -p "443:1443" \
    --restart="unless-stopped" \
    -e WEBCRATE_UID=$uid \
    -e WEBCRATE_GID=$gid \
    $PROJECTS_HOMES \
    -v /etc/localtime:/etc/localtime:ro \
    -v $(pwd)/projects.yml:/webcrate/projects.yml:ro \
    -v $(pwd)/var/letsencrypt:/webcrate/letsencrypt:ro \
    -v $(pwd)/var/letsencrypt-meta:/webcrate/letsencrypt-meta:ro \
    -v $(pwd)/var/openssl:/webcrate/openssl:ro \
    -v $(pwd)/var/logs/nginx:/webcrate/logs \
    -v $(pwd)/config/nginx:/webcrate/nginx-config:ro \
    -v webcrate_ssl_configs:/webcrate/ssl_configs:ro \
    -v webcrate_gzip_configs:/webcrate/gzip_configs:ro \
    -v webcrate_redirect_configs:/webcrate/redirect_configs:ro \
    -v webcrate_options_configs:/webcrate/options_configs:ro \
    -v webcrate_block_configs:/webcrate/block_configs:ro \
    -v webcrate_auth_locations_configs:/webcrate/auth_locations_configs:ro \
    -v webcrate_nginx_configs:/etc/nginx/conf.d:ro \
    ace5040/webcrate-nginx:stable > /dev/null
  for project_name in "${PROJECTS_LIST[@]}"
  do
    docker network connect webcrate_network_$project_name webcrate-nginx
  done
  docker start webcrate-nginx
fi

writeLog "Starting ftp container"
if docker container inspect webcrate-ftp >/dev/null 2> /dev/null; then
   writeLog "service webcrate-ftp exists"
else

  PROJECTS_HOMES=""
  for SITES_PATH in ${WEBCRATE_PROJECTS_FOLDERS[@]}
  do
    if [[ $SITES_PATH == /* ]]; then
      SITES_ABSOLUTE_PATH=$SITES_PATH;
    else
      SITES_ABSOLUTE_PATH=$(pwd)/$SITES_PATH;
    fi
    for dir in $(find $SITES_ABSOLUTE_PATH -mindepth 1 -maxdepth 1 -type d); do
      project_name=`basename $dir`
      PROJECTS_HOMES="$PROJECTS_HOMES-v $SITES_ABSOLUTE_PATH/$project_name:/home/$project_name "
    done
  done

  docker run -d --env-file=$(pwd)/.env --hostname webcrate-ftp --name webcrate-ftp \
    --network="host" \
    --restart="unless-stopped" \
    -e WEBCRATE_UID=$uid \
    -e WEBCRATE_GID=$gid \
    $PROJECTS_HOMES \
    -v /etc/localtime:/etc/localtime:ro \
    -v $(pwd)/projects.yml:/webcrate/projects.yml:ro \
    -v $(pwd)/var/meta:/webcrate/meta \
    ace5040/webcrate-ftp:stable > /dev/null
fi

writeLog "Starting webcrate-tools container"

if docker container inspect webcrate-tools >/dev/null 2> /dev/null; then
  writeLog "service webcrate-tools exists"
else
  docker run -d --env-file=$(pwd)/.env --hostname webcrate-tools --name webcrate-tools \
    --network="webcrate_network" --dns=10.255.0.100 \
    --restart="unless-stopped" \
    -e WEBCRATE_UID=$uid \
    -e WEBCRATE_GID=$gid \
    $PROJECTS_VOLUMES \
    -v $DOCKER_SOCKET:/var/run/docker.sock \
    -v /etc/localtime:/etc/localtime:ro \
    -v $(pwd):/webcrate-readonly:ro \
    -v $(pwd)/var/meta:/webcrate/meta \
    -v $(pwd)/projects.yml:/webcrate/projects.yml:ro \
    -v $(pwd)/services.yml:/webcrate/services.yml:ro \
    -v $(pwd)/var/letsencrypt:/webcrate/letsencrypt \
    -v $(pwd)/var/letsencrypt-meta:/webcrate/letsencrypt-meta \
    -v $(pwd)/var/openssl:/webcrate/openssl \
    -v $(pwd)/var/backup:/webcrate/backup \
    -v $(pwd)/var/secrets:/webcrate/secrets \
    -v $(pwd)/var/duplicity:/webcrate/duplicity \
    -v webcrate_ssl_configs:/webcrate/ssl_configs \
    -v $(pwd)/config/nginx-templates:/webcrate/nginx-templates:ro \
    -v $(pwd)/config/php-pool-templates:/webcrate/custom_templates:ro \
    -v webcrate_nginx_configs:/webcrate/nginx_configs \
    -v webcrate_gzip_configs:/webcrate/gzip_configs \
    -v webcrate_redirect_configs:/webcrate/redirect_configs \
    -v webcrate_options_configs:/webcrate/options_configs \
    -v webcrate_block_configs:/webcrate/block_configs \
    -v webcrate_auth_locations_configs:/webcrate/auth_locations_configs \
    -v webcrate_php_pools:/webcrate/php-fpm.d \
    -v webcrate_dnsmasq_hosts:/webcrate-dnsmasq/config \
    ace5040/webcrate-tools:stable > /dev/null
fi
