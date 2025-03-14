function Build() {

	BUILDTARGET=$1
	if [ "$BUILDTARGET" != "all" ]\
		&& [ "$BUILDTARGET" != "nginx" ]\
		&& [ "$BUILDTARGET" != "utils-pwgen" ]\
		&& [ "$BUILDTARGET" != "utils-docker" ]\
		&& [ "$BUILDTARGET" != "core" ]\
		&& [ "$BUILDTARGET" != "core-nginx" ]\
		&& [ "$BUILDTARGET" != "core-gunicorn" ]\
		&& [ "$BUILDTARGET" != "core-php83" ]\
		&& [ "$BUILDTARGET" != "core-php81" ]\
		&& [ "$BUILDTARGET" != "core-php74" ]\
		&& [ "$BUILDTARGET" != "core-php73" ]\
		&& [ "$BUILDTARGET" != "core-php56" ]\
		&& [ "$BUILDTARGET" != "admin" ]\
		&& [ "$BUILDTARGET" != "dnsmasq" ]\
		&& [ "$BUILDTARGET" != "stats" ]\
	;then
		echo "Unknown target $1. Please use one of: all, nginx, utils-pwgen, utils-docker, core, core-gunicorn, core-php83, core-php81, core-php74, core-php73, core-php56, admin, stats"
		exit 1
	fi

	LONGOPTS=no-cache,update-base-images,progress-plain
	OPTIONS=nup
	PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@") || exit 2
	eval set -- "$PARSED"
	BUILD_OPTIONS=''
	u=n
	while true; do
		case "$1" in
			-n|--no-cache)
				BUILD_OPTIONS=$BUILD_OPTIONS' --no-cache'
				shift
				;;
			-u|--update-base-images)
				u=y
				shift
				;;
			-p|--progress-plain)
				BUILD_OPTIONS=$BUILD_OPTIONS' --progress=plain'
				shift
				;;
			--)
				shift
				break
				;;
			*)
				echo "Programming error"
				exit 3
				;;
		esac
	done
	if [ $# -eq 1 ]
	then
		if [ "$u" = "y" ]
		then
			docker pull $IMAGE_ALPINE_BASE
			docker pull $IMAGE_DEBIAN_STABLE_SLIM
			docker pull $IMAGE_DEBIAN_SLIM
			docker pull $IMAGE_NGINX_BASE
		fi
	else
		echo "Wrong number of args"
		exit 4
	fi

	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "nginx" ]; then
		docker build -t $IMAGE_NGINX --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_NGINX_BASE ./src/nginx$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "core-nginx" ]; then
		docker build -t $IMAGE_CORE_NGINX --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_NGINX_BASE ./src/core-nginx$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "dnsmasq" ]; then
		docker build -t $IMAGE_DNSMASQ --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_ALPINE_BASE ./src/dnsmasq$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "utils-pwgen" ]; then
		docker build -t $IMAGE_UTILS_PWGEN --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_ALPINE_BASE ./src/utils-pwgen$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "utils-docker" ]; then
		docker build -t $IMAGE_UTILS_DOCKER --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_ALPINE_BASE ./src/utils-docker$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "core" ] || [ "$BUILDTARGET" = "core-php83" ]; then
		docker build -t $IMAGE_CORE_PHP83 --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_DEBIAN_STABLE_SLIM ./src/core-php83$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "core" ] || [ "$BUILDTARGET" = "core-php81" ]; then
		docker build -t $IMAGE_CORE_PHP81 --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_DEBIAN_STABLE_SLIM ./src/core-php81$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "core" ] || [ "$BUILDTARGET" = "core-php74" ]; then
		docker build -t $IMAGE_CORE_PHP74 --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_DEBIAN_STABLE_SLIM ./src/core-php74$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "core" ] || [ "$BUILDTARGET" = "core-php73" ]; then
		docker build -t $IMAGE_CORE_PHP73 --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_DEBIAN_STABLE_SLIM ./src/core-php73$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "core" ] || [ "$BUILDTARGET" = "core-php56" ]; then
		docker build -t $IMAGE_CORE_PHP56 --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_DEBIAN_STABLE_SLIM ./src/core-php56$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "core" ] || [ "$BUILDTARGET" = "core-gunicorn" ]; then
		docker build -t $IMAGE_CORE_GUNICORN --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_DEBIAN_SLIM ./src/core-gunicorn$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "admin" ]; then
		docker build -t $IMAGE_ADMIN --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_DEBIAN_STABLE_SLIM ./src/admin$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "stats" ]; then
		docker build -t $IMAGE_STATS --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_DEBIAN_STABLE_SLIM ./src/stats$BUILD_OPTIONS
	fi

}
