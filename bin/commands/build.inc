function Build() {

	BUILDTARGET=$1
	if [ "$BUILDTARGET" != "all" ]\
		&& [ "$BUILDTARGET" != "nginx" ]\
		&& [ "$BUILDTARGET" != "utils-pwgen" ]\
		&& [ "$BUILDTARGET" != "utils-docker" ]\
		&& [ "$BUILDTARGET" != "core" ]\
		&& [ "$BUILDTARGET" != "core-gunicorn" ]\
		&& [ "$BUILDTARGET" != "core-php83" ]\
		&& [ "$BUILDTARGET" != "core-php81" ]\
		&& [ "$BUILDTARGET" != "core-php74" ]\
		&& [ "$BUILDTARGET" != "core-php73" ]\
		&& [ "$BUILDTARGET" != "core-php56" ]\
		&& [ "$BUILDTARGET" != "admin" ]\
		&& [ "$BUILDTARGET" != "dnsmasq" ]\
		&& [ "$BUILDTARGET" != "ftp" ]\
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
			exit 2
			docker pull archlinux:base-20241027.0.273886
			docker pull $IMAGE_NGINX_BASE
		fi
	else
		echo "Wrong number of args"
		exit 4
	fi

	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "nginx" ]; then
		docker build -t $IMAGE_NGINX --build-arg IMAGE_NGINX_BASE=$IMAGE_NGINX_BASE ./src/nginx$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "dnsmasq" ]; then
		docker build -t $IMAGE_DNSMASQ --build-arg IMAGE_ALPINE_BASE=$IMAGE_ALPINE_BASE ./src/dnsmasq$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "utils-pwgen" ]; then
		docker build -t $IMAGE_UTILS_PWGEN --build-arg IMAGE_ALPINE_BASE=$IMAGE_ALPINE_BASE ./src/utils-pwgen$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "utils-docker" ]; then
		docker build -t $IMAGE_UTILS_DOCKER --build-arg IMAGE_ALPINE_BASE=$IMAGE_ALPINE_BASE ./src/utils-docker$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "core" ] || [ "$BUILDTARGET" = "core-php83" ]; then
		docker build -t $IMAGE_CORE_PHP83 --build-arg IMAGE=$IMAGE_DEBIAN_SLIM ./src/core-php83$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "core" ] || [ "$BUILDTARGET" = "core-php81" ]; then
		docker build -t $IMAGE_CORE_PHP81 --build-arg IMAGE=$IMAGE_DEBIAN_SLIM ./src/core-php81$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "core" ] || [ "$BUILDTARGET" = "core-php74" ]; then
		docker build -t $IMAGE_CORE_PHP74 --build-arg IMAGE=$IMAGE_DEBIAN_SLIM ./src/core-php74$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "core" ] || [ "$BUILDTARGET" = "core-php73" ]; then
		docker build -t $IMAGE_CORE_PHP73 --build-arg IMAGE=$IMAGE_DEBIAN_SLIM ./src/core-php73$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "core" ] || [ "$BUILDTARGET" = "core-php56" ]; then
		docker build -t $IMAGE_CORE_PHP56 --build-arg IMAGE=$IMAGE_DEBIAN_SLIM ./src/core-php56$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "core" ] || [ "$BUILDTARGET" = "core-gunicorn" ]; then
		docker build -t $IMAGE_CORE_GUNICORN --build-arg IMAGE_LINUX_BASE=$IMAGE_LINUX_BASE ./src/core-gunicorn$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "admin" ]; then
		docker build -t $IMAGE_ADMIN --build-arg IMAGE_LINUX_BASE=$IMAGE_LINUX_BASE ./src/admin$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "ftp" ]; then
		docker build -t $IMAGE_FTP --build-arg IMAGE_LINUX_BASE=$IMAGE_LINUX_BASE ./src/ftp$BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "stats" ]; then
		docker build -t $IMAGE_STATS --build-arg IMAGE_LINUX_BASE=$IMAGE_LINUX_BASE ./src/stats$BUILD_OPTIONS
	fi

}
