source /env.fish
set fish_greeting ""
set -x VISUAL mcedit
set -x EDITOR mcedit
set -x DRUSH_LAUNCHER_FALLBACK ~/.config/composer/vendor/bin/drush
set -x HOME ~
set PATH /webcrate-bin $PATH
set -x u $USER
if test -e ~/config.fish
    source ~/config.fish
end
if test -d $HOME/$DATA_FOLDER
    cd ~/$DATA_FOLDER
end
if test -d $HOME/$DATA_FOLDER/bin
    set PATH $HOME/$DATA_FOLDER/bin $PATH
end
pyenv init - | source
pyenv install -s 3.10.13
pyenv shell 3.10.13
