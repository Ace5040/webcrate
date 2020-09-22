set fish_greeting ""
set -x VISUAL mcedit
set -x DRUSH_LAUNCHER_FALLBACK ~/.composer/vendor/bin/drush
set PATH /webcrate/bin $PATH
set u (basename $PWD)
set DATA_FOLDER (cat /webcrate/users.yml | awk "/$u/,/backup/" | grep -oP "(?<=root_folder: ).*" | cut -d "/" -f1 | head -c -1)
if test -d $HOME/$DATA_FOLDER
    cd ~/$DATA_FOLDER
end
if test -d $HOME/$DATA_FOLDER/bin
    set PATH $HOME/$DATA_FOLDER/bin $PATH
end
if test -e ~/phpversion.fish
    . ~/phpversion.fish
end
