source ./bin/includes/functions.inc

function Configure() {

	validate_email() {
		local email="$1"
		if [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
			return 0
		else
			return 1
		fi
	}

	validate_country() {
		local country="$1"
		if [[ "$country" =~ ^[A-Za-z]{2}$ ]]; then
			return 0
		else
			return 1
		fi
	}

	validate_ip() {
		[[ "$1" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]
	}

	validate_port() {
		[[ "$1" =~ ^[0-9]+$ ]] && [ "$1" -ge 1 -a "$1" -le 65535 ]
	}

	validate_boolean() {
		[[ "$1" == "yes" || "$1" == "no" || "$1" == "y" || "$1" == "n" ]]
	}

	validate_number() {
		[[ "$1" =~ ^[0-9]+$ ]]
	}

	validate_path() {
		[[ "$1" =~ ^/ ]]
	}

	to_boolean() {
		if [[ "$1" == "yes" || "$1" == "y" ]]; then
			echo true
		else
			echo false
		fi
	}

	# create or rewrite .env file
	if [[ -f ".env" ]]; then
		while true; do
			read -p "$(t ".env already exits. Overwrite?") y/n [n]: " overwrite
			overwrite=${overwrite:-n}
			overwrite=${overwrite,,}
			validate_boolean "$overwrite" || continue
			if [[ "$overwrite" == "n" ]]; then
				t ".env creation canceled"
				exit 0
			else
				break
			fi
		done
	fi
	>| .env

	# select app mode
	while true; do
		read -p "$(t "Webcrate mode") dev/prod [prod]: " app_mode
		app_mode=${app_mode:-prod}
		app_mode=${app_mode,,}
		if [[ "$app_mode" == "dev" || "$app_mode" == "prod" ]]; then
			echo "WEBCRATE_APP_MODE=$app_mode" >> .env
			break
		else
			t "Only 'dev' or 'prod' are valid values"
		fi
	done

	# select log level
	while true; do
		read -p "$(t "Log level") debug/info/error [info]: " log_level
		log_level=${log_level:-info}
		log_level=${log_level,,}

		if [[ "$log_level" == "debug" || "$log_level" == "info" || "$log_level" == "error" ]]; then
			echo "WEBCRATE_LOG_LEVEL=$log_level" >> .env
			break
		else
			echo "Only 'debug', 'info' or 'error' are valid values"
		fi
	done

	# enter admin email
	while true; do
		read -p "$(t "Admin email(login)"): " admin_email

		if validate_email "$admin_email"; then
			echo "WEBCRATE_ADMIN_EMAIL=$admin_email" >> .env
			break
		else
			echo "Invalid email"
		fi
	done

	# enter country code
	while true; do
		read -p "$(t "Country code, e.g. US, RU, DE"): " country

		if validate_country "$country"; then
			# Приводим к верхнему регистру
			country=$(echo "$country" | tr '[:lower:]' '[:upper:]')
			echo "WEBCRATE_COUNTRY=$country" >> .env
			break
		else
			t "Enter two latin letters"
		fi
	done

	# enter organization
	while true; do
		read -p "Oragnization name: " organization

		if [[ -z "$organization" ]]; then
			t "Cannot be empty"
			continue
		else
			echo "WEBCRATE_ORGANIZATION=$organization" >> .env
			break
		fi
	done

	# ports settings
	while true; do
		read -p "WEBCRATE_APP_HTTP_PORT [80]: " http_port
		http_port=${http_port:-80}
		validate_port "$http_port" && break
		t "Port must be between 1 and 65535"
	done
	echo "WEBCRATE_APP_HTTP_PORT=$http_port" >> .env

	while true; do
		read -p "WEBCRATE_APP_HTTPS_PORT [443]: " https_port
		https_port=${https_port:-443}
		validate_port "$https_port" && break
		t "Port must be between 1 and 65535"
	done
	echo "WEBCRATE_APP_HTTPS_PORT=$https_port" >> .env

	while true; do
		read -p "$(t "Enable local DNS?") y/n [n]: " localdns
		localdns=${localdns:-n}
		localdns=${localdns,,}
		validate_boolean "$localdns" && break
	done
	echo "WEBCRATE_LOCALDNS=$(to_boolean $localdns)" >> .env

	while true; do
		read -p "DOCKER_HOST_IP (IP адрес машины): " docker_host_ip
		validate_ip "$docker_host_ip" && break
		echo "Must be correct IP address, e.g. 192.168.1.1"
	done
	echo "DOCKER_HOST_IP=$docker_host_ip" >> .env

	while true; do
		read -p "WEBCRATE_EXTERNAL_DNS_IP (IP адрес роутера): " external_dns_ip
		validate_ip "$external_dns_ip" && break
		echo "Must be correct IP address, e.g. 192.168.1.1"
	done
	echo "WEBCRATE_EXTERNAL_DNS_IP=$external_dns_ip" >> .env

	# Настройки Docker
	read -p "DOCKER_SOCKET [/var/run/docker.sock]: " docker_socket
	docker_socket=${docker_socket:-/var/run/docker.sock}
	echo "DOCKER_SOCKET=$docker_socket" >> .env

	# WEBCRATE_PROJECTS_FOLDERS
	echo -e "\nВведите пути к папкам проектов (по одному за раз)"
	echo "Оставьте пустым и нажмите Enter чтобы завершить ввод"
	projects_folders=()

	while true; do
		read -p "Путь к папке проекта (абсолютный или относительный): " project_path

		if [[ -z "$project_path" ]]; then
			if [[ ${#projects_folders[@]} -eq 0 ]]; then
				echo "Ошибка: должен быть указан хотя бы один путь"
				continue
			else
				break
			fi
		fi

		# Добавляем путь
		projects_folders+=("\"$project_path\"")
	done

	# Записываем в формате Bash-массива
	echo "WEBCRATE_PROJECTS_FOLDERS=(${projects_folders[@]})" >> .env

	# Настройки сервисов
	while true; do
		read -p "WEBCRATE_SERVICE_HTMLTOPDF (true/false) [false]: " htmltopdf
		htmltopdf=${htmltopdf:-false}
		validate_boolean "$htmltopdf" && break
		t "Must be 'true' or 'false'"
	done
	echo "WEBCRATE_SERVICE_HTMLTOPDF=$htmltopdf" >> .env

	while true; do
		read -p "WEBCRATE_SERVICE_DOCTOHTML (true/false) [false]: " doctohtml
		doctohtml=${doctohtml:-false}
		validate_boolean "$doctohtml" && break
		t "Must be 'true' or 'false'"
	done
	echo "WEBCRATE_SERVICE_DOCTOHTML=$doctohtml" >> .env

	while true; do
		read -p "WEBCRATE_SERVICE_STATS (true/false) [true]: " stats
		stats=${stats:-true}
		validate_boolean "$stats" && break
		t "Must be 'true' or 'false'"
	done
	echo "WEBCRATE_SERVICE_STATS=$stats" >> .env

	# Настройки бэкапов
	while true; do
		read -p "WEBCRATE_FULL_BACKUP_DAYS [30]: " backup_days
		backup_days=${backup_days:-30}
		validate_number "$backup_days" && break
		t "Must be a number"
	done
	echo "WEBCRATE_FULL_BACKUP_DAYS=$backup_days" >> .env

	while true; do
		read -p "WEBCRATE_MAX_FULL_BACKUPS [1]: " max_backups
		max_backups=${max_backups:-1}
		validate_number "$max_backups" && break
		t "Must be a number"
	done
	echo "WEBCRATE_MAX_FULL_BACKUPS=$max_backups" >> .env

	# URI для бэкапов
	echo "Введите URI для хранения резервных копий (по одному за раз)"
	echo "Оставьте пустым и нажмите Enter чтобы завершить ввод"
	backup_uris=()

	while true; do
		read -p "Дополнительные URI для бэкапа: " uri

		if [[ -z "$uri" ]]; then
			if [[ ${#backup_uris[@]} -eq 0 ]]; then
				echo "Ошибка: должен быть указан хотя бы один URI"
				continue
			else
				break
			fi
		else
			backup_uris+=("\"$uri\"")
		fi
	done

	echo "WEBCRATE_BACKUP_URIS=(${backup_uris[@]})" >> .env

	# URI для бэкапов
	echo "Введите URI для хранения резервных копий (по одному за раз)"
	echo "Оставьте пустым и нажмите Enter чтобы завершить ввод"
	backup_uris=()

	while true; do
		read -p "Дополнительные URI для бэкапа: " uri

		if [[ -z "$uri" ]]; then
			if [[ ${#backup_uris[@]} -eq 0 ]]; then
				echo "Ошибка: должен быть указан хотя бы один URI"
				continue
			else
				break
			fi
		else
			backup_uris+=("\"$uri\"")
		fi
	done

	echo "WEBCRATE_BACKUP_URIS=(${backup_uris[@]})" >> .env

}
