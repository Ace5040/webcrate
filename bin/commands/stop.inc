function Stop() {
	LONGOPTS=service
	OPTIONS=s:
	PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@") || exit 2
	if [ $# -eq 1 ]
	then
		if [[ ${ALLOWED_SERVICES[@]} =~ $1 ]]
		then
			echo "Stopping $1"
			docker stop webcrate-$1 > /dev/null
			docker container rm webcrate-$1 > /dev/null
			writeLog "Stopped and removed"
		else
			echo "Unknown service $1"
			exit 3
		fi
	elif [ $# -eq 0 ]
	then
		writeLog "Stopping and removing webcrate containers"
		containers=$(docker ps -a -q --filter name=webcrate-)
		if [ "$containers" != "" ]; then
			docker stop $containers > /dev/null
			docker container rm $containers > /dev/null
		fi
		writeLog "Removing networks"
		networks=$(docker network list -q --filter name=webcrate_)
		if [ "$networks" != "" ]; then
			docker network rm $networks > /dev/null
		fi
		writeLog "Stopped and removed"
	else
		echo "Wrong number of args"
		exit 4
	fi

}
