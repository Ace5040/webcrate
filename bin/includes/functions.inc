function generatePassword () {
  pass=`docker run --rm ace5040/webcrate-tools:stable /webcrate/pwgen.sh`
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

function writeLog () {
  if [[ ! -d "./var/log" ]] ; then mkdir -p "./var/log"; fi
  echo "$(date -Is):: $1"
  echo "$(date -Is):: $1" >> ./var/log/app.log
}
