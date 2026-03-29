function Backup() {
	writeLog "$(printf "$(t "Starting backup: %s %s")" "$1" "$2")" $LOG_LEVEL_INFO
	docker exec webcrate-utils-docker /backup.py $1 $2
	writeLog "$(printf "$(t "Backup finished: %s %s")" "$1" "$2")" $LOG_LEVEL_INFO
}
