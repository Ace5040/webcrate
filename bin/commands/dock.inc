function Dock() {

	LONGOPTS=root
	OPTIONS=r
	PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@") || exit 2
	eval set -- "$PARSED"
	r=n
	while true; do
		case "$1" in
			-r|--root)
				r=y
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
		if [ "$r" = "y" ]
		then
			docker exec --interactive --tty webcrate-core-${1} bash
		else
			docker exec --interactive --tty --user ${1} webcrate-core-${1} bash
		fi
	else
		writeLog "Wrong number of args" $LOG_LEVEL_ERROR
		exit 4
	fi

}
