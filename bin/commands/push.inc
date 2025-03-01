function Push() {

	IMAGE=$1
	if [ "$IMAGE" != "all" ]\
		&& [ "$IMAGE" != "nginx" ]\
		&& [ "$IMAGE" != "utils-pwgen" ]\
		&& [ "$IMAGE" != "utils-docker" ]\
		&& [ "$IMAGE" != "core" ]\
		&& [ "$IMAGE" != "core-gunicorn" ]\
		&& [ "$IMAGE" != "core-php83" ]\
		&& [ "$IMAGE" != "core-php81" ]\
		&& [ "$IMAGE" != "core-php74" ]\
		&& [ "$IMAGE" != "core-php73" ]\
		&& [ "$IMAGE" != "core-php56" ]\
		&& [ "$IMAGE" != "admin" ]\
		&& [ "$IMAGE" != "dnsmasq" ]\
		&& [ "$IMAGE" != "stats" ];\
	then
		echo "Unknown image $IMAGE. Please use one of: all, nginx, utils-pwgen, utils-docker, core, core-gunicorn, core-php83, core-php81, core-php74, core-php73, core-php56, admin, stats"
		exit 1
	fi
	if [ "$IMAGE" = "all" ] || [ "$IMAGE" = "nginx" ]; then
		docker push $IMAGE_NGINX
	fi
	if [ "$IMAGE" = "all" ] || [ "$IMAGE" = "utils-pwgen" ]; then
		docker push $IMAGE_UTILS_PWGEN
	fi
	if [ "$IMAGE" = "all" ] || [ "$IMAGE" = "utils-docker" ]; then
		docker push $IMAGE_UTILS_DOCKER
	fi
	if [ "$IMAGE" = "all" ] || [ "$IMAGE" = "core" ]; then
		docker push $IMAGE_CORE_PHP83
		docker push $IMAGE_CORE_PHP81
		docker push $IMAGE_CORE_PHP56
		docker push $IMAGE_CORE_PHP73
		docker push $IMAGE_CORE_PHP74
		docker push $IMAGE_CORE_GUNICORN
	fi
	if [ "$IMAGE" = "core-gunicorn" ]; then
		docker push $IMAGE_CORE_GUNICORN
	fi
	if [ "$IMAGE" = "core-php83" ]; then
		docker push $IMAGE_CORE_PHP83
	fi
	if [ "$IMAGE" = "core-php81" ]; then
		docker push $IMAGE_CORE_PHP81
	fi
	if [ "$IMAGE" = "core-php74" ]; then
		docker push $IMAGE_CORE_PHP74
	fi
	if [ "$IMAGE" = "core-php73" ]; then
		docker push $IMAGE_CORE_PHP73
	fi
	if [ "$IMAGE" = "core-php56" ]; then
		docker push $IMAGE_CORE_PHP56
	fi
	if [ "$IMAGE" = "all" ] || [ "$IMAGE" = "admin" ]; then
		docker push $IMAGE_ADMIN
	fi
	if [ "$IMAGE" = "all" ] || [ "$IMAGE" = "dnsmasq" ]; then
		docker push $IMAGE_DNSMASQ
	fi
	if [ "$IMAGE" = "all" ] || [ "$IMAGE" = "stats" ]; then
		docker push $IMAGE_STATS
	fi

}
