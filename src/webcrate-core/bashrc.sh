alias ls='ls --color=auto'
export VISUAL=mcedit
export DRUSH_LAUNCHER_FALLBACK=~/.composer/vendor/bin/drush
PATH=/webcrate-bin:$PATH
u=${HOME//\/sites\/}
export DATA_FOLDER=`cat /webcrate/users.yml | awk "/${u}:/,/backup:/" | grep -oP "(?<=root_folder: ).*" | cut -d "/" -f1 | head -c -1`
[ -d "$HOME/$DATA_FOLDER" ] && cd ~/$DATA_FOLDER;
[ -d "$HOME/$DATA_FOLDER/bin" ] && PATH=$HOME/$DATA_FOLDER/bin:$PATH;
[ -r ~/phpversion.sh ] && . ~/phpversion.sh
