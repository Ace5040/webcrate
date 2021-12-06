source /env.bash
export EDITOR=mcedit
export VISUAL=mcedit
export DRUSH_LAUNCHER_FALLBACK=~/.config/composer/vendor/bin/drush
export HOME=~
PATH=/webcrate-bin:$PATH
if test -e ~/config.sh; then
    source ~/config.sh
fi
[ -d "$HOME/$DATA_FOLDER" ] && cd ~/$DATA_FOLDER;
[ -d "$HOME/$DATA_FOLDER/bin" ] && PATH=$HOME/$DATA_FOLDER/bin:$PATH;
alias ls='ls --color=auto'
PS1='[$USER@\h \W]\$ '
