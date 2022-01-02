backends=( "gunicorn" "php56" "php73" "php74" "php" )
PROJECT_COUNT=1
for backend in "${backends[@]}"
do
  if [ -f ./var/meta/projects-$backend.list ]; then
    while read -r line; do
      project=($line)
      project_name=${project[0]}
      if docker network inspect webcrate_network_${project_name} >/dev/null 2> /dev/null; then
        writeLog "Network webcrate_network_${project_name} exists"
      else
        writeLog "Create docker network for ${project_name}"
        docker network create --driver=bridge --subnet=10.$PROJECT_COUNT.0.0/24 webcrate_network_${project_name} > /dev/null
      fi
      let PROJECT_COUNT+=1
    done < "./var/meta/projects-$backend.list"
  fi
done
PROJECT_COUNT=1
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
      project_password=${project[5]}
      memcached=${project[6]}
      solr=${project[7]}

      PROJECT_VOLUME=""
      PROJECT_SOLR=""
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
          if [ "$solr" = "True" ]; then
            SOLR_LOGS=$SITES_ABSOLUTE_PATH/$project_name/var/solr/logs
            SOLR_CORES=$SITES_ABSOLUTE_PATH/$project_name/var/solr/cores
            mkdir -p $SOLR_LOGS
            mkdir -p $SOLR_CORES
            PROJECT_SOLR="-v ${SOLR_LOGS}:/opt/solr/server/logs -v ${SOLR_CORES}:/opt/solr/server/solr/mycores"
          fi
          break
        fi
      done

      PHP_CONFIGS=""
      if [ "$backend" = "php56" ] || [ "$backend" = "php73" ] || [ "$backend" = "php74" ] || [ "$backend" = "php" ]; then
        PHP_CONFIGS="-v $(pwd)/config/php/$backend.ini:/etc/$backend/conf.d/user.ini:ro -v $(pwd)/var/php_pools/${backend}:/webcrate/pools"
      fi

      if docker container inspect $container_name >/dev/null 2> /dev/null; then
        writeLog "Core $container_name exists"
      else
        writeLog "Starting $container_name container for $project_name"
        if [[ ! -f "./var/crontabs/$project_name" ]] ; then
          echo "" > ./var/crontabs/$project_name
        fi
        docker run -d --env-file=$(pwd)/.env --hostname $container_name --name $container_name \
          --network="webcrate_network_${project_name}" --dns=10.$PROJECT_COUNT.0.250 \
          --restart="unless-stopped" \
          -p "$ssh_port:22" \
          -e WEBCRATE_UID=$uid \
          -e WEBCRATE_GID=$gid \
          -e WEBCRATE_PROJECT=$project_name \
          -e WEBCRATE_PROJECT_PASSWORD=$project_password \
          -e WEBCRATE_DOMAIN=$project_domain \
          -v /etc/localtime:/etc/localtime:ro \
          $PROJECT_VOLUME \
          -v $(pwd)/var/crontabs/$project_name:/var/spool/cron/$project_name \
          -v $(pwd)/config/telegraf:/etc/telegraf/telegraf.d:ro \
          -v $(pwd)/projects.yml:/webcrate/projects.yml:ro \
          -v $(pwd)/var/ssh:/webcrate/ssh_keys \
          -v $(pwd)/var/meta:/webcrate/meta \
          -v $(pwd)/var/log:/webcrate/log \
          -v $(pwd)/config/exim/exim.conf:/etc/mail/exim.original.conf \
          $PHP_CONFIGS \
          ace5040/$image_name:stable > /dev/null
      fi

      if [ "$memcached" = "True" ]; then
        if docker container inspect webcrate-memcached_$project_name >/dev/null 2> /dev/null; then
          writeLog "Container webcrate-memcached_${project_name} exists"
        else
          writeLog "Starting webcrate-memcached_${project_name} container"
          docker run -d --env-file=$(pwd)/.env --log-driver=none --name webcrate-memcached_$project_name \
            --network="webcrate_network_${project_name}" \
            --restart="unless-stopped" \
            memcached:1 > /dev/null
        fi
      fi

      if [ "$solr" = "True" ]; then
        if docker container inspect webcrate-solr_$project_name >/dev/null 2> /dev/null; then
          writeLog "Container webcrate-solr_${project_name} exists"
        else
          writeLog "Starting webcrate-solr_${project_name} container"
          docker run -d --env-file=$(pwd)/.env --log-driver=none --name webcrate-solr_$project_name \
            --network="webcrate_network_${project_name}" \
            --restart="unless-stopped" \
            --user "$uid:$gid" \
            -v /etc/localtime:/etc/localtime:ro \
            $PROJECT_SOLR \
            --entrypoint docker-entrypoint.sh \
            solr:6 solr -m 4096m -force -f > /dev/null
        fi
      fi

      docker network connect --ip=10.$PROJECT_COUNT.0.250 webcrate_network_${project_name} webcrate-dnsmasq
      docker network connect webcrate_network_$project_name webcrate-mysql5
      docker network connect webcrate_network_$project_name webcrate-mysql
      docker network connect webcrate_network_$project_name webcrate-postgres
      if [ "$WEBCRATE_SERVICE_DOCTOHTML" = true ]; then
        docker network connect webcrate_network_$project_name webcrate-doctohtml
      fi
      if [ "$WEBCRATE_SERVICE_HTMLTOPDF" = true ]; then
        docker network connect webcrate_network_$project_name webcrate-htmltopdf
      fi
      if [ "$WEBCRATE_SERVICE_STATS" = true ]; then
        docker network connect webcrate_network_$project_name webcrate-influxdb
      fi
      docker network connect webcrate_network_$project_name webcrate-nginx

      let PROJECT_COUNT+=1
    done < "./var/meta/projects-$backend.list"

  fi
done
