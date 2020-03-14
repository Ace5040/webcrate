alias ls='ls --color=auto'
VISUAL=mcedit
PATH=/sitesbox/bin:$PATH
DRUSH_LAUNCHER_FALLBACK=~/.composer/vendor/bin/drush
u=${HOME//\/sites\/}
[ -d "$HOME/$u.test" ] && cd ~/$u.test;
[ -d "$HOME/data" ] && cd ~/data;
[ -d "$HOME/app" ] && cd ~/app;
[ -r ~/phpversion.sh ] && . ~/phpversion.sh
