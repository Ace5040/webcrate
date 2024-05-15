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
alias mc="mc --nosubshell"
case $- in
  *i*) ;;
    *) return;;
esac
source /usr/share/blesh/ble.sh --noattach
export OSH=/usr/share/oh-my-bash
OSH_THEME="powerline"
DISABLE_AUTO_UPDATE="true"
OMB_USE_SUDO=true
aliases=(
  general
)
BASH_CACHE_DIR=$HOME/.cache/oh-my-bash
if [[ ! -d $BASH_CACHE_DIR ]]; then
	mkdir $BASH_CACHE_DIR
fi

source "$OSH"/oh-my-bash.sh

function __powerline_customcwd_prompt {
  echo "\w|${CWD_THEME_PROMPT_COLOR}"
}
function __powerline_project_prompt {
  echo "$USER@$WEBCRATE_DOMAIN|${USER_INFO_THEME_PROMPT_COLOR}"
}

POWERLINE_PROMPT="clock project scm customcwd"
[[ ${BLE_VERSION-} ]] && ble-attach
ble-face syntax_error="fg=203"
ble-face auto_complete="fg=238"
bleopt prompt_eol_mark=''
bleopt exec_errexit_mark=
bleopt edit_marker=
bleopt edit_marker_error=
bleopt exec_elapsed_mark=
pyenv init - | source
pyenv install -s 3.10.13
pyenv shell 3.10.13
