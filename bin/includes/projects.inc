if [[ -d ./var/meta/projects && -n "$(ls -A ./var/meta/projects)" ]]; then
  for projectConfig in ./var/meta/projects/*.config
  do
    while read -r line; do
      project=($line)
      project_name=${project[1]}
      writeLog "Starting project $project_name"
      docker run --rm --env-file=$(pwd)/.env \
        --name webcrate-utils-docker-$project_name \
        -e WEBCRATE_UID=$uid \
        -e WEBCRATE_GID=$gid \
        -e WEBCRATE_SERVICE_STATS=$WEBCRATE_SERVICE_STATS \
        -e WEBCRATE_LOCALDNS=$WEBCRATE_LOCALDNS \
        -e WEBCRATE_SERVICE_DOCTOHTML=$WEBCRATE_SERVICE_DOCTOHTML \
        -e WEBCRATE_SERVICE_HTMLTOPDF=$WEBCRATE_SERVICE_HTMLTOPDF \
        $PROJECTS_VOLUMES \
        -e WEBCRATE_PROJECTS_FOLDERS=$( IFS=:; printf '%s' "${WEBCRATE_PROJECTS_FOLDERS[*]}" ) \
        -e WEBCRATE_PWD=$(pwd) \
        -v $DOCKER_SOCKET:/var/run/docker.sock \
        -v $(pwd):/webcrate-readonly:ro \
        -v $(pwd)/projects.yml:/webcrate/projects.yml:ro \
        -v $(pwd)/var/log:/webcrate/log \
        -v $(pwd)/var/meta:/webcrate/meta \
        -v $(pwd)/var/nginx:/webcrate/nginx \
        -v $(pwd)/var/secrets:/webcrate/secrets \
        -v $(pwd)/var/mysql-projects:/webcrate/mysql-projects \
        -v $(pwd)/var/mysql5-projects:/webcrate/mysql5-projects \
        -v $(pwd)/var/postgresql-projects:/webcrate/postgresql-projects \
        -v $(pwd)/var/openssl:/webcrate/openssl \
        -v $(pwd)/var/letsencrypt:/webcrate/letsencrypt \
        -v $(pwd)/var/letsencrypt-meta:/webcrate/letsencrypt-meta \
        -v $(pwd)/var/crontabs:/webcrate/crontabs \
        -v $(pwd)/var/php_pools:/webcrate/php_pools \
        $IMAGE_UTILS_DOCKER /project-start.py $project_name
      writeLog "Project $project_name started"
    done < $projectConfig
  done
fi
