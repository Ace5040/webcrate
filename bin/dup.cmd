cd c:\sitesbox

docker run --rm --env-file=%cd%\.env -v C:\projects:/sites -v %cd%/sites:/sitesbox/sites_configs:ro -v %cd%/config/php-pool-templates:/sitesbox/custom_templates:ro -v sitesbox_nginx_configs_volume:/sitesbox/nginx_configs -v sitesbox_php7_pools_volume:/sitesbox/php-fpm.d -v sitesbox_php73_pools_volume:/sitesbox/php73-fpm.d -v sitesbox_php5_pools_volume:/sitesbox/php56-fpm.d  ace5040/utils:stable /sitesbox/generate_configs.sh

docker run --rm --env-file=%cd%\.env -v sitesbox_dnsmasq_hosts_volume:/sitesbox/dnsmasq_hosts -v sitesbox_nginx_configs_volume:/sitesbox/nginx_configs:ro ace5040/utils:stable /sitesbox/generate_hosts.sh

docker-compose up -d
