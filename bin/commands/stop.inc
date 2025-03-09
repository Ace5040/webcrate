function Stop() {
	LONGOPTS=service
	OPTIONS=s:
	PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@") || exit 2
	if [ $# -eq 1 ]
	then
		if [[ ${ALLOWED_SERVICES[@]} =~ $1 ]]
		then
			writeLog "Stopping $1" $LOG_LEVEL_INFO
			docker stop webcrate-$1 > /dev/null
			docker container rm webcrate-$1 > /dev/null
			writeLog "$1 stopped and removed" $LOG_LEVEL_INFO
		else
			writeLog "Unknown service $1" $LOG_LEVEL_ERROR
			exit 3
		fi
	elif [ $# -eq 0 ]
	then
		writeLog "Stopping and removing webcrate containers" $LOG_LEVEL_INFO
		containers=$(docker ps -a -q --filter name=webcrate-)
		if [ "$containers" != "" ]; then
			docker stop $containers > /dev/null
			docker container rm $containers > /dev/null
		fi
		writeLog "Removing networks" $LOG_LEVEL_INFO
		networks=$(docker network list -q --filter name=webcrate_)
		if [ "$networks" != "" ]; then
			docker network rm $networks > /dev/null
		fi
		writeLog "Stopped and removed" $LOG_LEVEL_INFO
	else
		writeLog "Wrong number of args" $LOG_LEVEL_ERROR
		exit 4
	fi

}
