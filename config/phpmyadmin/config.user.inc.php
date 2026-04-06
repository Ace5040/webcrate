<?php

$hostsFile = '/webcrate/meta/dbhosts.txt';
$hosts = file_exists($hostsFile)
    ? array_filter(array_map('trim', explode(',', file_get_contents($hostsFile))))
    : [];

foreach ($hosts as $i => $host) {
    $idx = $i + 1;
    $cfg['Servers'][$idx]['host'] = $host;
    $cfg['Servers'][$idx]['auth_type'] = 'cookie';
    $cfg['Servers'][$idx]['hide_db'] = 'information_schema|performance_schema|mysql';
}
