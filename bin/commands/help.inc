function Help() {

	echo ''
	echo "$(t "Usage: webcrate _command_ [OPTIONS]")"
	echo ''
	echo "$(t "  configure - Build config and start containers")"
	echo "$(t "  start     - Build config and start containers")"
	echo "$(t "  stop      - Stop and remove all containers")"
	echo "$(t "  restart   - Same as Stop then Start")"
	echo "$(t "  dock      - Connect to project container with bash. Usage webcrate dock [project_name]")"
	echo "$(t "              if project_name is not preset connects as root")"
	echo "$(t "  update    - Update all images from dockerhub and pull fresh source from github")"
	echo "$(t "  pull      - Update all images from dockerhub")"
	echo "$(t "  log       - Print all docker logs")"
	echo "$(t "  backup    - Start backup process manually")"
	echo "$(t "  build     - Build images from source. Usage webcrate build [OPTIONS] target")"
	echo "$(t "                target: can be one of nginx, core, core-nginx, core-gunicorn, core-php84, core-php83, core-php81, core-php74, core-php73, core-php56, utils-pwgen, utils-docker, admin, dnsmasq or all")"
	echo "$(t "                OPTIONS:")"
	echo "$(t "                  -c, --no-cache : do not use docker build cache")"
	echo "$(t "                  -u, --update-base-images : pulls fresh base images before build")"
	echo "$(t "                  -p, --progress-plain : make build progress plain")"
	echo "$(t "  push      - Push images to dockerhub. Usage webcrate push _image_")"
	echo "$(t "                _image_: can be one of nginx, core, utils-pwgen, utils-docker, admin or all")"
	echo "$(t "  help      - Print this info")"
	echo ''

}
