set fish_greeting ""
set -x VISUAL mcedit
set -x DRUSH_LAUNCHER_FALLBACK ~/.composer/vendor/bin/drush
set PATH /webcrate-bin $PATH
set u (basename $PWD)
if test -e ~/config.fish
    . ~/config.fish
end
if test -d $HOME/$DATA_FOLDER
    cd ~/$DATA_FOLDER
end
if test -d $HOME/$DATA_FOLDER/bin
    set PATH $HOME/$DATA_FOLDER/bin $PATH
end
