set VISUAL mcedit
set PATH /sitesbox/bin $PATH
set DRUSH_LAUNCHER_FALLBACK ~/.composer/vendor/bin/drush
set u (basename $PWD)
set fish_greeting ""
if test -d $HOME/$u.test
    cd ~/$u.test
end
if test -d $HOME/data
    cd ~/data
end
if test -d $HOME/app
    cd ~/app
end
if test -e ~/phpversion.fish
    . ~/phpversion.fish
end
