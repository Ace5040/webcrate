if docker container inspect webcrate-nginx >/dev/null 2> /dev/null; then
  writeLog "Container webcrate-nginx exists"
else
  writeLog "Starting nginx container"
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
  docker run -d --env-file=$(pwd)/.env --hostname webcrate-nginx --name webcrate-nginx \
    --network="webcrate_network" \
    -p "${WEBCRATE_APP_HTTP_PORT}:1080" \
    -p "${WEBCRATE_APP_HTTPS_PORT}:1443" \
    --restart="unless-stopped" \
    -e WEBCRATE_UID=$uid \
    -e WEBCRATE_GID=$gid \
    $PROJECTS_HOMES \
    -v /etc/localtime:/etc/localtime:ro \
    -v $(pwd)/config/nginx:/webcrate/nginx-config:ro \
    -v $(pwd)/var/nginx:/webcrate/nginx:ro \
    -v $(pwd)/var/nginx/confs:/etc/nginx/conf.d:ro \
    -v $(pwd)/var/letsencrypt:/webcrate/letsencrypt:ro \
    -v $(pwd)/var/letsencrypt-meta:/webcrate/letsencrypt-meta:ro \
    -v $(pwd)/var/openssl:/webcrate/openssl:ro \
    -v $(pwd)/var/log/nginx:/webcrate/log \
    $IMAGE_NGINX > /dev/null
fi

if docker container inspect webcrate-dnsmasq >/dev/null 2> /dev/null; then
  writeLog "Service webcrate-dnsmasq exists"
else
  writeLog "Starting webcrate-dnsmasq container"
  DNSPORT=""
  if [ "$WEBCRATE_LOCALDNS" = true ]; then
    DNSPORT=-p\ "53:53/udp"
  fi
  docker run -d --hostname webcrate-dnsmasq --name webcrate-dnsmasq \
    --network="webcrate_network" --ip=10.255.0.100 \
    --restart="unless-stopped" \
    $DNSPORT \
    -v $(pwd)/var/dnsmasq:/dnsmasq \
    $IMAGE_DNSMASQ > /dev/null
fi

writeLog "Init services"
docker run --rm --env-file=$(pwd)/.env \
  --name webcrate-utils-docker-services-init \
  -e WEBCRATE_UID=$uid \
  -e WEBCRATE_GID=$gid \
  -e WEBCRATE_SERVICE_STATS=$WEBCRATE_SERVICE_STATS \
  -e WEBCRATE_LOCALDNS=$WEBCRATE_LOCALDNS \
  -e WEBCRATE_SERVICE_DOCTOHTML=$WEBCRATE_SERVICE_DOCTOHTML \
  -e WEBCRATE_SERVICE_HTMLTOPDF=$WEBCRATE_SERVICE_HTMLTOPDF \
  -e WEBCRATE_PWD=$(pwd) \
  -v $DOCKER_SOCKET:/var/run/docker.sock \
  -v $(pwd):/webcrate-readonly:ro \
  -v $(pwd)/services.yml:/webcrate/services.yml:ro \
  -v $(pwd)/projects.yml:/webcrate/projects.yml:ro \
  -v $(pwd)/var/log:/webcrate/log \
  -v $(pwd)/var/meta:/webcrate/meta \
  -v $(pwd)/var/secrets:/webcrate/secrets \
  -v $(pwd)/var/mysql-services:/webcrate/mysql-services \
  -v $(pwd)/var/openssl:/webcrate/openssl \
  -v $(pwd)/var/letsencrypt:/webcrate/letsencrypt \
  -v $(pwd)/var/letsencrypt-meta:/webcrate/letsencrypt-meta \
  -v $(pwd)/var/crontabs:/webcrate/crontabs \
  -v $(pwd)/var/php_pools:/webcrate/php_pools \
  $IMAGE_UTILS_DOCKER /services-init.py
writeLog "Services inited"

if docker container inspect webcrate-mysql >/dev/null 2> /dev/null; then
  writeLog "Container webcrate-mysql exists"
else
  writeLog "Starting webcrate-mysql container"
  if [ "$MYSQL_ROOT_PASS" != "" ]; then MYSQL_ROOT_PASS=-e\ MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASS"; fi
  docker run -d --env-file=$(pwd)/.env --name webcrate-mysql \
    --network="webcrate_network" --dns=10.255.0.100 \
    --restart="unless-stopped" \
    --user "$uid:$gid" \
    $MYSQL_ROOT_PASS \
    -v /etc/localtime:/etc/localtime:ro \
    -v $(pwd)/var/mysql:/var/lib/mysql \
    -v $(pwd)/config/mysql/mysql.cnf:/etc/mysql/conf.d/user.cnf \
    $IMAGE_MARIADB10 > /dev/null
fi

if docker container inspect webcrate-mysql5 >/dev/null 2> /dev/null; then
  writeLog "Container webcrate-mysql5 exists"
else
  writeLog "Starting webcrate-mysql5 container"
  if [ "$MYSQL5_ROOT_PASS" != "" ]; then MYSQL5_ROOT_PASS=-e\ MYSQL5_ROOT_PASSWORD="$MYSQL5_ROOT_PASS"; fi
  docker run -d --env-file=$(pwd)/.env --name webcrate-mysql5 \
    --network="webcrate_network" --dns=10.255.0.100 \
    --restart="unless-stopped" \
    --user "$uid:$gid" \
    $MYSQL5_ROOT_PASS \
    -v /etc/localtime:/etc/localtime:ro \
    -v $(pwd)/var/mysql5:/var/lib/mysql \
    -v $(pwd)/config/mysql/mysql5.cnf:/etc/mysql/conf.d/user.cnf \
    $IMAGE_MARIADB5 > /dev/null
fi

if docker container inspect webcrate-postgres >/dev/null 2> /dev/null; then
  writeLog "Container webcrate-postgres exists"
else
  writeLog "Starting webcrate-postgres container"
  if [ "$POSTGRES_PASS" != "" ]; then POSTGRES_PASS=-e\ POSTGRES_PASSWORD="$POSTGRES_PASS"; fi
  docker run -d --env-file=$(pwd)/.env --name webcrate-postgres \
    --network="webcrate_network" --dns=10.255.0.100 \
    --restart="unless-stopped" \
    --user "$uid:$gid" \
    $POSTGRES_PASS \
    -v $(pwd)/var/postgres:/var/lib/postgresql/data \
    $IMAGE_POSTGRES > /dev/null
fi

if docker container inspect webcrate-admin >/dev/null 2> /dev/null; then
  writeLog "Container webcrate-admin exists"
else
  writeLog "Starting webcrate-admin container"
  if [ "$WEBCRATE_APP_MODE" = "DEV" ]; then WEBCRATE_APP_SRC=-v\ $(pwd)/src/admin/app:/app; else WEBCRATE_APP_SRC=""; fi
  docker run -d --env-file=$(pwd)/.env --hostname webcrate-admin --name webcrate-admin \
    --network="webcrate_network" --dns=10.255.0.100 \
    --restart="unless-stopped" \
    -e WEBCRATE_UID=$uid \
    -e WEBCRATE_GID=$gid \
    -e WEBCRATE_PROJECTS_FOLDERS=$( IFS=:; printf '%s' "${WEBCRATE_PROJECTS_FOLDERS[*]}" ) \
    -v /etc/localtime:/etc/localtime:ro \
    -v $DOCKER_SOCKET:/var/run/docker.sock \
    $WEBCRATE_APP_SRC \
    -v $(pwd)/var/meta:/webcrate/meta \
    -v $(pwd)/var/log:/webcrate/log \
    -v $(pwd)/var/secrets:/webcrate/secrets \
    -v $(pwd)/projects.yml:/webcrate/projects.yml \
    -v $(pwd)/redirects.yml:/webcrate/redirects.yml \
    -v $(pwd)/services.yml:/webcrate/services.yml \
    $IMAGE_ADMIN > /dev/null
fi

if docker container inspect webcrate-phpmyadmin >/dev/null 2> /dev/null; then
  writeLog "Container webcrate-phpmyadmin exists"
else
  writeLog "Starting webcrate-phpmyadmin container"
  PMA_HOSTS=`cat $(pwd)/var/meta/dbhosts.txt`
  docker run -d --env-file=$(pwd)/.env --name webcrate-phpmyadmin \
    --network="webcrate_network" --dns=10.255.0.100 \
    --restart="unless-stopped" \
    -e PMA_HOSTS=$PMA_HOSTS \
    -e UPLOAD_LIMIT=2048M \
    -v /etc/localtime:/etc/localtime:ro \
    -v $(pwd)/config/phpmyadmin/php.ini:/usr/local/etc/php/php.ini:ro \
    -v $(pwd)/config/phpmyadmin/config.user.inc.php:/etc/phpmyadmin/config.user.inc.php:ro \
    $IMAGE_PHPMYADMIN > /dev/null
fi

# if docker container inspect webcrate-phppgadmin >/dev/null 2> /dev/null; then
#   writeLog "Container webcrate-phppgadmin exists"
# else
#   writeLog "Starting webcrate-phppgadmin container"
#   docker run -d --env-file=$(pwd)/.env --name webcrate-phppgadmin \
#     --network="webcrate_network" --dns=10.255.0.100 \
#     --restart="unless-stopped" \
#     -v /etc/localtime:/etc/localtime:ro \
#     dockage/phppgadmin > /dev/null
#     # $IMAGE_PHPPGADMIN > /dev/null
# fi

if [ "$WEBCRATE_SERVICE_DOCTOHTML" = true ]; then
  if docker container inspect webcrate-doctohtml >/dev/null 2> /dev/null; then
    writeLog "Container webcrate-doctohtml exists"
  else
    writeLog "Starting webcrate-doctohtml container"
    docker run -d --env-file=$(pwd)/.env --name webcrate-doctohtml \
      --network="webcrate_network" --dns=10.255.0.100 \
      --restart="unless-stopped" \
      -p "3000:3000" \
      $IMAGE_DOCTOHTML > /dev/null
  fi
fi

if [ "$WEBCRATE_SERVICE_HTMLTOPDF" = true ]; then
  if docker container inspect webcrate-htmltopdf >/dev/null 2> /dev/null; then
    writeLog "Container webcrate-htmltopdf exists"
  else
    writeLog "Starting webcrate-htmltopdf container"
    docker run -d --env-file=$(pwd)/.env --name webcrate-htmltopdf \
      --network="webcrate_network" --dns=10.255.0.100 \
      --restart="unless-stopped" \
      -p "3001:3000" \
      $IMAGE_HTMLTOPDF > /dev/null
  fi
fi

if [ "$WEBCRATE_SERVICE_STATS" = true ]; then
  if docker container inspect webcrate-grafana >/dev/null 2>/dev/null; then
    writeLog "Container grafana exists"
  else
    writeLog "Starting graphana container"
    docker run -d --env-file=$(pwd)/.env --name webcrate-grafana \
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
      $IMAGE_GRAPHANA >/dev/null 2>/dev/null
  fi
  if docker container inspect webcrate-influxdb >/dev/null 2>/dev/null; then
    writeLog "Container webcrate-influxdb exists"
  else
    writeLog "Starting webcrate-influxdb container"
    docker run -d --env-file=$(pwd)/.env --name webcrate-influxdb \
      --network="webcrate_network" --dns=10.255.0.100 \
      --restart="unless-stopped" \
      --user "$uid:$gid" \
      -e DOCKER_INFLUXDB_INIT_MODE=setup \
      -e DOCKER_INFLUXDB_INIT_USERNAME=influxdb \
      -e DOCKER_INFLUXDB_INIT_PASSWORD=influxdb \
      -e DOCKER_INFLUXDB_INIT_ORG=webcrate \
      -e DOCKER_INFLUXDB_INIT_BUCKET=webcrate \
      -e DOCKER_INFLUXDB_INIT_RETENTION=180d \
      -e DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=webcrate \
      -v /etc/localtime:/etc/localtime:ro \
      -v $(pwd)/var/influxdb/data:/var/lib/influxdb2 \
      -v $(pwd)/var/influxdb/etc:/etc/influxdb2 \
      $IMAGE_INFLUXDB >/dev/null 2>/dev/null
  fi
  if [ "$GRAFANA_PASS" != "" ]; then
    sleep 10; docker exec --user $uid:$gid webcrate-grafana grafana-cli admin reset-admin-password "$GRAFANA_PASS"
  fi
fi

if docker container inspect webcrate-ftp >/dev/null 2>/dev/null; then
  writeLog "Container webcrate-ftp exists"
else
  writeLog "Starting ftp container"
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
    -v $(pwd)/var/log:/webcrate/log \
    $IMAGE_FTP > /dev/null
fi

if docker container inspect webcrate-utils-docker >/dev/null 2>/dev/null; then
  writeLog "Container webcrate-utils-docker exists"
else
  writeLog "Starting webcrate-utils-docker container"
  docker run -d --env-file=$(pwd)/.env --hostname webcrate-utils-docker --name webcrate-utils-docker \
    --network="webcrate_network" --dns=10.255.0.100 \
    --restart="unless-stopped" \
    -e WEBCRATE_UID=$uid \
    -e WEBCRATE_GID=$gid \
    -e WEBCRATE_PWD=$(pwd) \
    $PROJECTS_VOLUMES \
    -e WEBCRATE_PROJECTS_FOLDERS=$( IFS=:; printf '%s' "${WEBCRATE_PROJECTS_FOLDERS[*]}" ) \
    -e WEBCRATE_BACKUP_URIS=$( IFS=^; printf '%s' "${WEBCRATE_BACKUP_URIS[*]}" ) \
    -v $DOCKER_SOCKET:/var/run/docker.sock \
    -v /etc/localtime:/etc/localtime:ro \
    -v $(pwd):/webcrate-readonly:ro \
    -v $(pwd)/var/log:/webcrate/log \
    -v $(pwd)/var/meta:/webcrate/meta \
    -v $(pwd)/var/crontabs:/webcrate/crontabs \
    -v $(pwd)/projects.yml:/webcrate/projects.yml:ro \
    -v $(pwd)/redirects.yml:/webcrate/redirects.yml:ro \
    -v $(pwd)/services.yml:/webcrate/services.yml:ro \
    -v $(pwd)/var/letsencrypt:/webcrate/letsencrypt \
    -v $(pwd)/var/letsencrypt-meta:/webcrate/letsencrypt-meta \
    -v $(pwd)/var/openssl:/webcrate/openssl \
    -v $WEBCRATE_BACKUP_ABSOLUTE_PATH:/webcrate/backup \
    -v $(pwd)/var/backup-tmp:/webcrate/backup-tmp \
    -v $(pwd)/var/mysql-projects:/webcrate/mysql-projects \
    -v $(pwd)/var/mysql5-projects:/webcrate/mysql5-projects \
    -v $(pwd)/var/postgresql-projects:/webcrate/postgresql-projects \
    -v $(pwd)/var/secrets:/webcrate/secrets \
    -v $(pwd)/var/duplicity:/webcrate/duplicity \
    -v $(pwd)/var/dnsmasq:/webcrate/dnsmasq \
    -v $(pwd)/config/php-pool-templates:/webcrate/custom_templates:ro \
    -v $(pwd)/config/nginx-templates:/webcrate/nginx-templates:ro \
    -v $(pwd)/var/nginx:/webcrate/nginx \
    -v $(pwd)/var/php_pools:/webcrate/php_pools \
    $IMAGE_UTILS_DOCKER >/dev/null
fi

if docker container inspect webcrate-stats >/dev/null 2> /dev/null; then
  writeLog "Container webcrate-stats exists"
else
  writeLog "Starting webcrate-stats container"
  docker run -d --env-file=$(pwd)/.env --hostname webcrate-stats --name webcrate-stats \
    --network="webcrate_network" --dns=10.255.0.100 \
    --restart="unless-stopped" \
    $PROJECTS_VOLUMES \
    -v $DOCKER_SOCKET:/var/run/docker.sock \
    -v /etc/localtime:/etc/localtime:ro \
    $IMAGE_STATS > /dev/null
fi
