alias ls='ls --color=auto'
export VISUAL=mcedit
export DRUSH_LAUNCHER_FALLBACK=~/.composer/vendor/bin/drush
PATH=/webcrate-bin:$PATH
u=$(whoami)
[ -r ~/config.sh ] && . ~/config.sh
[ -d "$HOME/$DATA_FOLDER" ] && cd ~/$DATA_FOLDER;
[ -d "$HOME/$DATA_FOLDER/bin" ] && PATH=$HOME/$DATA_FOLDER/bin:$PATH;

