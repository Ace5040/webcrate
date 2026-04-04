function Backup() {
	local arg1="${1:-all}"
	local arg2="${2:-all}"
	writeLog "$(printf "$(t "Starting backup: %s %s")" "$arg1" "$arg2")" $LOG_LEVEL_INFO
	docker exec webcrate-utils-docker /backup.py $arg1 $arg2
	writeLog "$(printf "$(t "Backup finished: %s %s")" "$arg1" "$arg2")" $LOG_LEVEL_INFO
}
