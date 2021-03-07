source /env.bash
export EDITOR=mcedit
export VISUAL=mcedit
export DRUSH_LAUNCHER_FALLBACK=~/.composer/vendor/bin/drush
PATH=/webcrate-bin:$PATH
if test -e ~/config.sh; then
    source ~/config.sh
fi
[ -d "$HOME/$DATA_FOLDER" ] && cd ~/$DATA_FOLDER;
[ -d "$HOME/$DATA_FOLDER/bin" ] && PATH=$HOME/$DATA_FOLDER/bin:$PATH;
alias ls='ls --color=auto'
if [ "$WEBCRATE_MODE" == "DEV" ]; then
    crontab()
    {
        sudo bash -c "EDITOR=mcedit crontab -u $USER $1"
    }
fi
PS1='[$USER@\h \W]\$ '
