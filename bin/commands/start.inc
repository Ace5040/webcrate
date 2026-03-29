function Start() {
	if [ $# -eq 1 ]
	then
		if [[ ${ALLOWED_SERVICES[@]} =~ $1 ]]
		then
			writeLog "$(printf "$(t "Starting %s service")" "$1")" $LOG_LEVEL_INFO
			source ./bin/includes/generate-config.inc
			source ./bin/includes/services.inc
			writeLog "$(t "Started")" $LOG_LEVEL_INFO
		else
			writeLog "$(printf "$(t "Unknown service: %s")" "$1")" $LOG_LEVEL_ERROR
			exit 1
		fi
	elif [ $# -eq 0 ]
	then
		writeLog "$(t "Starting all services")" $LOG_LEVEL_INFO
		source ./bin/includes/generate-config.inc
		source ./bin/includes/services.inc
		source ./bin/includes/projects.inc
		writeLog "$(t "Started")" $LOG_LEVEL_INFO
	else
		writeLog "$(t "Wrong number of args")" $LOG_LEVEL_ERROR
		exit 1
	fi

}
