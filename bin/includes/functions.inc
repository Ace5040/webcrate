#debug | info | error
LOG_LEVEL_DEBUG=9
LOG_LEVEL_INFO=6
LOG_LEVEL_ERROR=3

LOG_LEVEL_VALUE=$LOG_LEVEL_ERROR

if [ "$WEBCRATE_LOG_LEVEL" = "debug" ]; then
	LOG_LEVEL_VALUE=$LOG_LEVEL_DEBUG
fi
if [ "$WEBCRATE_LOG_LEVEL" = "info" ]; then
	LOG_LEVEL_VALUE=$LOG_LEVEL_INFO
fi
if [ "$WEBCRATE_LOG_LEVEL" = "error" ]; then
	LOG_LEVEL_VALUE=$LOG_LEVEL_ERROR
fi

function generatePassword () {
	pass=`docker run --rm $IMAGE_UTILS_PWGEN -e LOG_LEVEL_VALUE=$LOG_LEVEL_VALUE /pwgen.sh`
	echo "[mysqldump]" > ./var/secrets/$1.cnf
	echo "user=root" >> ./var/secrets/$1.cnf
	echo "password=\"$pass\"" >> ./var/secrets/$1.cnf
	chmod 0600 ./var/secrets/$1.cnf
	echo $pass
}

function initDbFolder () {
	if [[ ! -d "./var/$1" ]] || [ ! "$(ls -A ./var/$1)" ] ; then
		if [[ ! -f "./var/secrets/$1.cnf" ]]; then
			echo $(generatePassword $1)
		fi
	fi
	echo ''
}

#$1 - message $2 - log level
function writeLog () {
	if [ "$LOG_LEVEL_VALUE" -ge "$2" ]; then
		echo "$(date -Is):: $1"
		echo "$(date -Is):: $1" >> ./var/log/app.log
	fi
}
