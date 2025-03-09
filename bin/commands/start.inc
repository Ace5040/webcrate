function Start() {
	if [ $# -eq 1 ]
	then
		if [[ ${ALLOWED_SERVICES[@]} =~ $1 ]]
		then
			writeLog "Starting $1 service" $LOG_LEVEL_INFO
			source ./bin/includes/generate-config.inc
			source ./bin/includes/services.inc
			writeLog "Started" $LOG_LEVEL_INFO
		else
			writeLog "Unknown service $1" $LOG_LEVEL_ERROR
			exit 1
		fi
	elif [ $# -eq 0 ]
	then
		writeLog "Starting All services" $LOG_LEVEL_INFO
		source ./bin/includes/generate-config.inc
		source ./bin/includes/services.inc
		source ./bin/includes/projects.inc
		writeLog "Started" $LOG_LEVEL_INFO
	else
		writeLog "Wrong number of args" $LOG_LEVEL_ERROR
		exit 1
	fi

}
