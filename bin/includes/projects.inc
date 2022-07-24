for projectConfig in ./var/meta/projects/*.config
do
  while read -r line; do
    project=($line)
    project_name=${project[1]}
    writeLog "Starting project $project_name"
    docker run --rm --env-file=$(pwd)/.env \
      -e WEBCRATE_UID=$uid \
      -e WEBCRATE_GID=$gid \
      -e WEBCRATE_SERVICE_STATS=$WEBCRATE_SERVICE_STATS \
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
      -v $(pwd)/var/letsencrypt:/webcrate/letsencrypt \
      -v $(pwd)/var/letsencrypt-meta:/webcrate/letsencrypt-meta \
      -v $(pwd)/var/crontabs:/webcrate/crontabs \
      -v $(pwd)/var/php_pools:/webcrate/php_pools \
      ace5040/webcrate-tools:stable /webcrate/scripts/project-start.py $project_name
    writeLog "Project $project_name started"
  done < $projectConfig
done
