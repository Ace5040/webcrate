function Pull() {

	docker pull $IMAGE_CORE_PHP56
	docker pull $IMAGE_CORE_PHP73
	docker pull $IMAGE_CORE_PHP74
	docker pull $IMAGE_CORE_PHP81
	docker pull $IMAGE_CORE_PHP83
	docker pull $IMAGE_CORE_GUNICORN
	docker pull $IMAGE_ADMIN
	docker pull $IMAGE_UTILS_PWGEN
	docker pull $IMAGE_UTILS_DOCKER
	docker pull $IMAGE_NGINX
	docker pull $IMAGE_DNSMASQ
	docker pull $IMAGE_STATS
	docker pull $IMAGE_DOCTOHTML
	docker pull $IMAGE_HTMLTOPDF
	docker pull $IMAGE_MEMCACHED
	docker pull $IMAGE_MARIADB5
	docker pull $IMAGE_MARIADB10
	docker pull $IMAGE_PHPMYADMIN
	docker pull $IMAGE_POSTGRES
	docker pull $IMAGE_PHPPGADMIN
	docker pull $IMAGE_SOLR
	docker pull $IMAGE_ELASTICSEARCH
	docker pull $IMAGE_GRAPHANA
	docker pull $IMAGE_INFLUXDB

}
