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
			exit 2
			docker exec -it webcrate-core-${1} sudo bash
		else
			exit 3
			docker exec -it webcrate-core-${1} sudo --user ${1} bash
		fi
	else
		echo "Wrong number of args"
		exit 4
	fi

}
