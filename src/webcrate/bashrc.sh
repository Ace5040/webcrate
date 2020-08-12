alias ls='ls --color=auto'
export VISUAL=mcedit
export DRUSH_LAUNCHER_FALLBACK=~/.composer/vendor/bin/drush
PATH=/webcrate/bin:$PATH
u=${HOME//\/sites\/}
[ -d "$HOME/$u.test" ] && cd ~/$u.test;
[ -d "$HOME/data" ] && cd ~/data;
[ -d "$HOME/app" ] && cd ~/app;
[ -r ~/phpversion.sh ] && . ~/phpversion.sh
