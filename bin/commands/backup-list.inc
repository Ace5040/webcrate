function BackupList() {
	local arg1="${1:-all}"
	writeLog "$(printf "$(t "Getting backups list: %s %s")" "$arg1")" $LOG_LEVEL_INFO
	docker exec webcrate-utils-docker /backup-list.py $arg1
	writeLog "$(printf "$(t "Getting backups list finished: %s %s")" "$arg1")" $LOG_LEVEL_INFO
}
