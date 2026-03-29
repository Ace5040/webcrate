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
			read -p "$(t ".env already exists. Overwrite?") y/n [n]: " overwrite
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
			echo "$(t "Only 'debug', 'info' or 'error' are valid values")"
		fi
	done

	# enter admin email
	while true; do
		read -p "$(t "Admin email(login)"): " admin_email

		if validate_email "$admin_email"; then
			echo "WEBCRATE_ADMIN_EMAIL=$admin_email" >> .env
			break
		else
			echo "$(t "Invalid email")"
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
		read -p "$(t "Organization name"): " organization

		if [[ -z "$organization" ]]; then
			t "Cannot be empty"
			echo ""
			continue
		else
			echo "WEBCRATE_ORGANIZATION=$organization" >> .env
			break
		fi
	done

	# ports settings
	while true; do
		read -p "$(t "HTTP port [80]"): " http_port
		http_port=${http_port:-80}
		validate_port "$http_port" && break
		t "Port must be between 1 and 65535"
	done
	echo "WEBCRATE_APP_HTTP_PORT=$http_port" >> .env

	while true; do
		read -p "$(t "HTTPS port [443]"): " https_port
		https_port=${https_port:-443}
		validate_port "$https_port" && break
		t "Port must be between 1 and 65535"
	done
	echo "WEBCRATE_APP_HTTPS_PORT=$https_port" >> .env

	while true; do
		read -p "$(t "Enable local DNS?") (yes/no) [no]: " localdns
		localdns=${localdns:-n}
		localdns=${localdns,,}
		validate_boolean "$localdns" && break
	done
	echo "WEBCRATE_LOCALDNS=$(to_boolean $localdns)" >> .env

	docker_host_ip=""
	while $(to_boolean $localdns); do
		read -p "$(t "Docker host IP address (machine IP)"): " docker_host_ip
		validate_ip "$docker_host_ip" && break
		echo "$(t "Must be a valid IP address, e.g. 192.168.1.1")"
	done
	echo "DOCKER_HOST_IP=$docker_host_ip" >> .env

	external_dns_ip=""
	while $(to_boolean $localdns); do
		read -p "$(t "External DNS IP address (router IP)"): " external_dns_ip
		validate_ip "$external_dns_ip" && break
		echo "$(t "Must be a valid IP address, e.g. 192.168.1.1")"
	done
	echo "WEBCRATE_EXTERNAL_DNS_IP=$external_dns_ip" >> .env

	# Настройки Docker
	read -p "$(t "Docker socket [/var/run/docker.sock]"): " docker_socket
	docker_socket=${docker_socket:-/var/run/docker.sock}
	echo "DOCKER_SOCKET=$docker_socket" >> .env

	# WEBCRATE_PROJECTS_FOLDERS
	echo -e "\n$(t "Enter project folder paths (e.g. projects), one per line")"
	echo "$(t "Leave empty and press Enter to finish")"
	projects_folders=()

	while true; do
		read -p "$(t "Enter absolute path (starting with /) or relative (placed in webcrate/var)"): " project_path

		if [[ -z "$project_path" ]]; then
			if [[ ${#projects_folders[@]} -eq 0 ]]; then
				echo "$(t "Error: at least one path must be specified")"
				continue
			else
				break
			fi
		fi

		# Добавляем путь
		[[ "$project_path" == /* ]] || project_path="var/$project_path"
		projects_folders+=("\"$project_path\"")
	done

	# Записываем в формате Bash-массива
	echo "WEBCRATE_PROJECTS_FOLDERS=(${projects_folders[@]})" >> .env

	# Настройки сервисов
	while true; do
		read -p "$(t "HTMLTOPDF service (yes/no) [no]"): " htmltopdf
		htmltopdf=${htmltopdf:-n}
		htmltopdf=${htmltopdf,,}
		validate_boolean "$htmltopdf" && break
		t "Must be 'yes(y)' or 'no(n)'"
	done
	echo "WEBCRATE_SERVICE_HTMLTOPDF=$(to_boolean $htmltopdf)" >> .env

	while true; do
		read -p "$(t "DOCTOHTML service (yes/no) [no]"): " doctohtml
		doctohtml=${doctohtml:-n}
		doctohtml=${doctohtml,,}
		validate_boolean "$doctohtml" && break
		t "Must be 'yes(y)' or 'no(n)'"
	done
	echo "WEBCRATE_SERVICE_DOCTOHTML=$(to_boolean $doctohtml)" >> .env

	while true; do
		read -p "$(t "STATS service (yes/no) [yes]"): " stats
		stats=${stats:-y}
		stats=${stats,,}
		validate_boolean "$stats" && break
		t "Must be 'yes(y)' or 'no(n)'"
	done
	echo "WEBCRATE_SERVICE_STATS=$(to_boolean $stats)" >> .env

	# Настройки бэкапов
	while true; do
		read -p "$(t "Full backup interval in days [30]"): " backup_days
		backup_days=${backup_days:-30}
		validate_number "$backup_days" && break
		t "Must be a number"
	done
	echo "WEBCRATE_FULL_BACKUP_DAYS=$backup_days" >> .env

	while true; do
		read -p "$(t "Maximum number of full backups [1]"): " max_backups
		max_backups=${max_backups:-1}
		validate_number "$max_backups" && break
		t "Must be a number"
	done
	echo "WEBCRATE_MAX_FULL_BACKUPS=$max_backups" >> .env

	# URI для бэкапов
	echo "$(t "Enter backup URIs (ftp://[user[:password]@]host[:port]/[/]path), one per line")"
	echo "$(t "If no URIs specified, backups will be stored in webcrate/var/backup")"
	echo "$(t "Leave empty and press Enter to finish")"
	backup_uris=()

	while true; do
		read -p "$(t "Additional backup URI"): " uri

		if [[ -z "$uri" ]]; then
			break
		else
			backup_uris+=("\"$uri\"")
		fi
	done

	echo "WEBCRATE_BACKUP_URIS=(${backup_uris[@]})" >> .env

}
