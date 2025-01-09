function Log() {

	docker ps -q | xargs -L 1 docker logs -t

}
