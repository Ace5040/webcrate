function Configure() {

	# Функция для валидации email
	validate_email() {
		local email="$1"
		if [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
			return 0
		else
			return 1
		fi
	}

	# Функция для валидации кода страны
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
		[[ "$1" == "true" || "$1" == "false" ]]
	}

	validate_number() {
		[[ "$1" =~ ^[0-9]+$ ]]
	}

	validate_path() {
		[[ "$1" =~ ^/ ]]
	}

	if [[ -f ".env" ]]; then
		while true; do
			read -p "Файл уже существует. Перезаписать? (y/n) [n]: " overwrite
			overwrite=${overwrite:-n}

			if [[ "$overwrite" == "y" || "$overwrite" == "Y" ]]; then
				break
			elif [[ "$overwrite" == "n" || "$overwrite" == "N" ]]; then
				echo "Создание .env файла отменено."
				exit 0
			else
				echo "Пожалуйста, введите y или n"
			fi
		done
	fi

	# Создаем или очищаем .env файл
	>| .env

	# WEBCRATE_APP_MODE
	while true; do
		read -p "APP mode (dev/prod) [prod]: " app_mode
		app_mode=${app_mode:-prod}

		if [[ "$app_mode" == "dev" || "$app_mode" == "prod" ]]; then
			echo "WEBCRATE_APP_MODE=$app_mode" >> .env
			break
		else
			echo "Ошибка: допустимые значения только 'dev' или 'prod'"
		fi
	done

	# WEBCRATE_LOG_LEVEL
	while true; do
		read -p "Log level (debug/info/error) [info]: " log_level
		log_level=${log_level:-info}

		if [[ "$log_level" == "debug" || "$log_level" == "info" || "$log_level" == "error" ]]; then
			echo "WEBCRATE_LOG_LEVEL=$log_level" >> .env
			break
		else
			echo "Ошибка: допустимые значения только 'debug', 'info' или 'error'"
		fi
	done

	# WEBCRATE_ADMIN_EMAIL
	while true; do
		read -p "Admin email(login): " admin_email

		if validate_email "$admin_email"; then
			echo "WEBCRATE_ADMIN_EMAIL=$admin_email" >> .env
			break
		else
			echo "Ошибка: введите корректный email (например, user@example.com)"
		fi
	done

	# WEBCRATE_COUNTRY
	while true; do
		read -p "Сountry Name (двухбуквенный код страны, например, US, RU, DE): " country

		if validate_country "$country"; then
			# Приводим к верхнему регистру
			country=$(echo "$country" | tr '[:lower:]' '[:upper:]')
			echo "WEBCRATE_COUNTRY=$country" >> .env
			break
		else
			echo "Ошибка: введите двухбуквенный код страны (например, US, RU, DE)"
		fi
	done

	# WEBCRATE_ORGANIZATION
	while true; do
		read -p "Организация: " country

		if [[ -z "$country" ]]; then
			echo "Ошибка: организация не может быть пустой"
			continue
		else
			echo "WEBCRATE_ORGANIZATION=$country" >> .env
			break
		fi
	done



	# Настройки портов
	while true; do
		read -p "WEBCRATE_APP_HTTP_PORT [80]: " http_port
		http_port=${http_port:-80}
		validate_port "$http_port" && break
		echo "Ошибка: порт должен быть числом от 1 до 65535"
	done
	echo "WEBCRATE_APP_HTTP_PORT=$http_port" >> .env

	while true; do
		read -p "WEBCRATE_APP_HTTPS_PORT [443]: " https_port
		https_port=${https_port:-443}
		validate_port "$https_port" && break
		echo "Ошибка: порт должен быть числом от 1 до 65535"
	done
	echo "WEBCRATE_APP_HTTPS_PORT=$https_port" >> .env

	# Настройки сети и DNS
	while true; do
		read -p "WEBCRATE_LOCALDNS (true/false) [true]: " localdns
		localdns=${localdns:-true}
		validate_boolean "$localdns" && break
		echo "Ошибка: допустимые значения только 'true' или 'false'"
	done
	echo "WEBCRATE_LOCALDNS=$localdns" >> .env

	while true; do
		read -p "DOCKER_HOST_IP (IP адрес машины): " docker_host_ip
		validate_ip "$docker_host_ip" && break
		echo "Ошибка: введите корректный IP адрес (например, 192.168.1.1)"
	done
	echo "DOCKER_HOST_IP=$docker_host_ip" >> .env

	while true; do
		read -p "WEBCRATE_EXTERNAL_DNS_IP (IP адрес роутера): " external_dns_ip
		validate_ip "$external_dns_ip" && break
		echo "Ошибка: введите корректный IP адрес (например, 192.168.1.1)"
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
		echo "Ошибка: допустимые значения только 'true' или 'false'"
	done
	echo "WEBCRATE_SERVICE_HTMLTOPDF=$htmltopdf" >> .env

	while true; do
		read -p "WEBCRATE_SERVICE_DOCTOHTML (true/false) [false]: " doctohtml
		doctohtml=${doctohtml:-false}
		validate_boolean "$doctohtml" && break
		echo "Ошибка: допустимые значения только 'true' или 'false'"
	done
	echo "WEBCRATE_SERVICE_DOCTOHTML=$doctohtml" >> .env

	while true; do
		read -p "WEBCRATE_SERVICE_STATS (true/false) [true]: " stats
		stats=${stats:-true}
		validate_boolean "$stats" && break
		echo "Ошибка: допустимые значения только 'true' или 'false'"
	done
	echo "WEBCRATE_SERVICE_STATS=$stats" >> .env

	# Настройки бэкапов
	while true; do
		read -p "WEBCRATE_FULL_BACKUP_DAYS [30]: " backup_days
		backup_days=${backup_days:-30}
		validate_number "$backup_days" && break
		echo "Ошибка: введите число"
	done
	echo "WEBCRATE_FULL_BACKUP_DAYS=$backup_days" >> .env

	while true; do
		read -p "WEBCRATE_MAX_FULL_BACKUPS [1]: " max_backups
		max_backups=${max_backups:-1}
		validate_number "$max_backups" && break
		echo "Ошибка: введите число"
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
