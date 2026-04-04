function BackupSave() {
	local arg1="${1:-all}"
	local arg2="${2:-}"
	local arg3="${3:-}"
	writeLog "$(printf "$(t "Saving backup: %s %s")" "$arg1" "$arg2" "$arg3")" $LOG_LEVEL_INFO
	docker exec webcrate-utils-docker /backup-save.py $arg1 $arg2 $arg3
	writeLog "$(printf "$(t "Saving backup finished: %s %s")" "$arg1" "$arg2" "$arg3")" $LOG_LEVEL_INFO
}
