function Backup() {
	writeLog "Start backup $1 $2" $LOG_LEVEL_INFO
	docker exec webcrate-utils-docker /backup.py $1 $2
	writeLog "Backup $1 $2 finished" $LOG_LEVEL_INFO
}
