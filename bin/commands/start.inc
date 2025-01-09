function Start() {

	if [ $# -eq 1 ]
	then
		if [[ ${ALLOWED_SERVICES[@]} =~ $1 ]]
		then
			echo "Starting $1"
			exit 0
		else
			echo "Unknown service $1"
			exit 3
		fi
	elif [ $# -eq 0 ]
	then
		echo "Starting All services"
		source ./bin/includes/generate-config.inc
		source ./bin/includes/services.inc
		source ./bin/includes/projects.inc
		writeLog "Started"
	else
		echo "Wrong number of args"
		exit 4
	fi

}
