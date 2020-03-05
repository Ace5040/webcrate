alias ls='ls --color=auto'
export VISUAL=mcedit
PATH=/sitesbox/bin:$PATH
u=${HOME//\/sites\/}
[ -d "$HOME/$u.test" ] && cd ~/$u.test;
[ -d "$HOME/data" ] && cd ~/data;
[ -d "$HOME/app" ] && cd ~/app;
