if docker container inspect webcrate-core >/dev/null 2> /dev/null; then
  echo service webcrate-core exists
else
  if [ "$WEBCRATE_MODE" == "DEV" ]; then
    WDS=-p\ "8080:8080/tcp";
    DNS_MASQ=-p\ "53:53/udp";
    FTP='';
  else
    WDS='';
    DNS_MASQ='';
    FTP=-p\ "21:21"\ -p\ "20:20"\ -p\ "50000-50100:50000-50100";
  fi

  docker run -d --env-file=$(pwd)/.env --hostname webcrate-core --name webcrate-core \
    --network="webcrate_network" --dns=172.31.0.100 --ip=172.31.0.100 \
    --restart="unless-stopped" \
    $WDS \
    $FTP \
    $DNS_MASQ \
    -p "2222:22" \
    -e WEBCRATE_UID=$uid \
    -e WEBCRATE_GID=$gid \
    -v /etc/localtime:/etc/localtime:ro \
    $PROJECTS_VOLUMES \
    -v $(pwd)/var/crontabs:/var/spool/cron \
    -v $(pwd)/config/telegraf:/etc/telegraf/telegraf.d:ro \
    -v $(pwd)/projects.yml:/webcrate/projects.yml:ro \
    -v $(pwd)/var/ssh:/webcrate/ssh_keys \
    -v $(pwd)/config/php-pool-templates:/webcrate/custom_templates:ro \
    -v $(pwd)/config/php/php56.ini:/etc/php56/conf.d/user.ini:ro \
    -v $(pwd)/config/php/php73.ini:/etc/php73/conf.d/user.ini:ro \
    -v $(pwd)/config/php/php74.ini:/etc/php74/conf.d/user.ini:ro \
    -v $(pwd)/config/php/php80.ini:/etc/php/conf.d/user.ini:ro \
    -v $(pwd)/config/exim/exim.conf:/etc/mail/exim.original.conf \
    -v webcrate_php56_pools:/etc/php56/php-fpm.d \
    -v webcrate_php73_pools:/etc/php73/php-fpm.d \
    -v webcrate_php74_pools:/etc/php74/php-fpm.d \
    -v webcrate_php80_pools:/etc/php/php-fpm.d \
    -v webcrate_dnsmasq_hosts:/webcrate-dnsmasq/config \
    ace5040/webcrate-core:stable > /dev/null
fi

if docker container inspect webcrate >/dev/null 2> /dev/null; then
  echo service webcrate exists
else
  if [ "$WEBCRATE_APP_MODE" == "DEV" ]; then WEBCRATE_APP_SRC=-v\ $(pwd)/src/webcrate-admin/app:/app; else WEBCRATE_APP_SRC=""; fi
  docker run -d --env-file=$(pwd)/.env --hostname webcrate --name webcrate \
    --network="webcrate_network" --dns=172.31.0.100 \
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

if [ "$WEBCRATE_SERVICE_MEMCACHED" = true ]; then
  if docker container inspect memcached >/dev/null 2> /dev/null; then
    echo service memcached exists
  else
    docker run -d --env-file=$(pwd)/.env --log-driver=none --name memcached \
      --network="webcrate_network" --dns=172.31.0.100 \
      --restart="unless-stopped" \
      memcached:1 > /dev/null
  fi
fi

if docker container inspect mysql5 >/dev/null 2> /dev/null; then
  echo service mysql5 exists
else
  if [ "$MYSQL5_ROOT_PASS" != "" ]; then MYSQL5_ROOT_PASS=-e\ MYSQL_ROOT_PASSWORD="$MYSQL5_ROOT_PASS"; fi
  docker run -d --env-file=$(pwd)/.env --name mysql5 \
    --network="webcrate_network" --dns=172.31.0.100 \
    --restart="unless-stopped" \
    --user "$uid:$gid" \
    $MYSQL5_ROOT_PASS \
    -p "3305:3306" \
    -v /etc/localtime:/etc/localtime:ro \
    -v $(pwd)/var/mysql5:/var/lib/mysql \
    -v $(pwd)/config/mysql/mysql5.cnf:/etc/mysql/conf.d/user.cnf \
    mariadb:5 > /dev/null
fi

if docker container inspect mysql >/dev/null 2> /dev/null; then
  echo service mysql exists
else
  if [ "$MYSQL_ROOT_PASS" != "" ]; then MYSQL_ROOT_PASS=-e\ MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASS"; fi
  docker run -d --env-file=$(pwd)/.env --name mysql \
    --network="webcrate_network" --dns=172.31.0.100 \
    --restart="unless-stopped" \
    --user "$uid:$gid" \
    $MYSQL_ROOT_PASS \
    -p "3306:3306" \
    -v /etc/localtime:/etc/localtime:ro \
    -v $(pwd)/var/mysql:/var/lib/mysql \
    -v $(pwd)/config/mysql/mysql.cnf:/etc/mysql/conf.d/user.cnf \
    mariadb:10 > /dev/null
fi

if docker container inspect postgres >/dev/null 2> /dev/null; then
  echo service postgres exists
else
  if [ "$POSTGRES_PASS" != "" ]; then POSTGRES_PASS=-e\ POSTGRES_PASSWORD="$POSTGRES_PASS"; fi
  docker run -d --env-file=$(pwd)/.env --name postgres \
    --network="webcrate_network" --dns=172.31.0.100 \
    --restart="unless-stopped" \
    --user "$uid:$gid" \
    $POSTGRES_PASS \
    -p "5432:5432" \
    -v $(pwd)/var/postgres:/var/lib/postgresql/data \
    postgres:12 > /dev/null
fi

if docker container inspect phpmyadmin >/dev/null 2> /dev/null; then
  echo service phpmyadmin exists
else
  docker run -d --env-file=$(pwd)/.env --name phpmyadmin \
    --network="webcrate_network" --dns=172.31.0.100 \
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

if docker container inspect phppgadmin >/dev/null 2> /dev/null; then
  echo service phppgadmin exists
else
  docker run -d --env-file=$(pwd)/.env --name phppgadmin \
    --network="webcrate_network" --dns=172.31.0.100 \
    --restart="unless-stopped" \
    -e DATABASE_HOST=postgres \
    -v /etc/localtime:/etc/localtime:ro \
    -v webcrate_phppgadmin:/bitnami \
    bitnami/phppgadmin:7 > /dev/null
fi

if [ "$WEBCRATE_SERVICE_DOCTOHTML" = true ]; then
  if docker container inspect doctohtml >/dev/null 2> /dev/null; then
    echo service doctohtml exists
  else
    docker run -d --env-file=$(pwd)/.env --name doctohtml \
      --network="webcrate_network" --dns=172.31.0.100 \
      --restart="unless-stopped" \
      -p "3000:3000" \
      ace5040/doctohtml:latest > /dev/null
  fi
fi

if [ "$WEBCRATE_SERVICE_HTMLTOPDF" = true ]; then
  if docker container inspect htmltopdf >/dev/null 2> /dev/null; then
    echo service htmltopdf exists
  else
    docker run -d --env-file=$(pwd)/.env --name htmltopdf \
      --network="webcrate_network" --dns=172.31.0.100 \
      --restart="unless-stopped" \
      -p "3001:3000" \
      ace5040/htmltopdf:latest > /dev/null
  fi
fi

if [ "$WEBCRATE_SERVICE_SOLR" = true ]; then
  if docker container inspect solr >/dev/null 2> /dev/null; then
    echo service solr exists
  else
    docker run -d --env-file=$(pwd)/.env --log-driver=none --name solr \
      --network="webcrate_network" --dns=172.31.0.100 \
      --restart="unless-stopped" \
      --user "$uid:$gid" \
      -p "8983:8983" \
      -v /etc/localtime:/etc/localtime:ro \
      -v $(pwd)/var/solr/logs:/opt/solr/server/logs \
      -v $(pwd)/var/solr/cores:/opt/solr/server/solr/mycores \
      --entrypoint docker-entrypoint.sh \
      solr:6 solr -m 4096m -force -f > /dev/null
  fi
fi

if [ "$WEBCRATE_SERVICE_STATS" = true ]; then
  if docker container inspect grafana >/dev/null 2> /dev/null; then
    echo service grafana exists
  else
    docker run -d --env-file=$(pwd)/.env --log-driver=none --name grafana \
      --network="webcrate_network" --dns=172.31.0.100 \
      --restart="unless-stopped" \
      --user "$uid:$gid" \
      -e GF_PATHS_DATA=/data \
      -e GF_PATHS_LOGS=/log \
      -e GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/home.json \
      -p "8181:3000" \
      -v /etc/localtime:/etc/localtime:ro \
      -v $(pwd)/var/grafana/data:/data \
      -v $(pwd)/var/grafana/log:/log \
      -v $(pwd)/config/grafana/home.json:/home.json \
      -v $(pwd)/config/grafana/dashboard.yml:/etc/grafana/provisioning/dashboards/default.yml \
      -v $(pwd)/config/grafana/datasource.yml:/etc/grafana/provisioning/datasources/default.yml \
      grafana/grafana:7.4.3 > /dev/null
  fi

  if docker container inspect influxdb >/dev/null 2> /dev/null; then
    echo service influxdb exists
  else
    docker run -d --env-file=$(pwd)/.env --log-driver=none --name influxdb \
      --network="webcrate_network" --dns=172.31.0.100 \
      --restart="unless-stopped" \
      --user "$uid:$gid" \
      -e INFLUXDB_DB=telegraf \
      -v /etc/localtime:/etc/localtime:ro \
      -v $(pwd)/var/influxdb:/var/lib/influxdb \
      influxdb:1.8-alpine > /dev/null
  fi
fi

if [ "$WEBCRATE_SERVICE_SYNAPSE" = true ]; then
  if docker container inspect synapse >/dev/null 2> /dev/null; then
    echo service synapse exists
  else
    turn_secret=`cat ./var/secrets/turn.secret`

    if [[ ! -f "./var/synapse/homeserver.yaml" ]] ; then
      docker run -it --rm --hostname synapse --name synapse \
        --user "$uid:$gid" \
        --network="webcrate_network" --dns=172.31.0.100 \
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
      --network="webcrate_network" --dns=172.31.0.100 \
      --restart="unless-stopped" \
      --user "$uid:$gid" \
      -e UID=$uid \
      -e GID=$gid \
      -v $(pwd)/var/synapse:/data \
      -v $(pwd)/var/openssl:/webcrate/openssl \
      matrixdotorg/synapse:latest
  fi

  if docker container inspect turn >/dev/null 2> /dev/null; then
    echo service turn exists
  else
    docker run -d --hostname turn --name turn \
      --network="webcrate_network" --dns=172.31.0.100 \
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
    echo service synapse-admin exists
  else
    docker run -d --env-file=$(pwd)/.env --hostname synapse-admin --name synapse-admin \
      --network="webcrate_network" --dns=172.31.0.100 \
      --restart="unless-stopped" \
      awesometechnologies/synapse-admin:latest

    if [ "$GRAFANA_PASS" != "" ]; then
      sleep 10; docker exec --user $uid:$gid grafana grafana-cli admin reset-admin-password "$GRAFANA_PASS"
    fi

    if [ "$SYNAPSE_PASS" != "" ]; then
      sleep 10; docker exec synapse register_new_matrix_user -a --user admin --password "$SYNAPSE_PASS" -c /data/homeserver.yaml http://localhost:8008
    fi
  fi
fi

if docker container inspect webcrate-nginx >/dev/null 2> /dev/null; then
  echo service webcrate-nginx exists
else
  docker run -d --env-file=$(pwd)/.env --hostname webcrate-nginx --name webcrate-nginx \
    --network="webcrate_network" --dns=172.31.0.100 \
    --restart="unless-stopped" \
    -e WEBCRATE_UID=$uid \
    -e WEBCRATE_GID=$gid \
    -p "80:1080" \
    -p "443:1443" \
    $PROJECTS_VOLUMES \
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
fi

if docker container inspect webcrate-tools >/dev/null 2> /dev/null; then
  echo service webcrate-tools exists
else
  docker run -d --env-file=$(pwd)/.env --hostname webcrate-tools --name webcrate-tools \
    --network="webcrate_network" --dns=172.31.0.100 \
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
    -v webcrate_php56_pools:/webcrate/php56-fpm.d \
    -v webcrate_php73_pools:/webcrate/php73-fpm.d \
    -v webcrate_php74_pools:/webcrate/php74-fpm.d \
    -v webcrate_php80_pools:/webcrate/php80-fpm.d \
    -v webcrate_dnsmasq_hosts:/webcrate-dnsmasq/config \
    ace5040/webcrate-tools:stable > /dev/null
fi
