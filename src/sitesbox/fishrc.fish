set -g __fish_git_prompt_color_branch magenta
set -g __fish_git_prompt_showupstream "informative"
set -g __fish_git_prompt_char_upstream_ahead "↑"
set -g __fish_git_prompt_char_upstream_behind "↓"
set -g __fish_git_prompt_char_upstream_prefix ""

set -g __fish_git_prompt_char_stagedstate "●"
set -g __fish_git_prompt_char_dirtystate "✚"
set -g __fish_git_prompt_char_untrackedfiles "…"
set -g __fish_git_prompt_char_conflictedstate "✖"
set -g __fish_git_prompt_char_cleanstate "✔"

set -g __fish_git_prompt_color_dirtystate blue
set -g __fish_git_prompt_color_stagedstate yellow
set -g __fish_git_prompt_color_invalidstate red
set -g __fish_git_prompt_color_untrackedfiles $fish_color_normal
set -g __fish_git_prompt_color_cleanstate green

set -g __fish_git_prompt_hide_untrackedfiles 1
set -g __fish_git_prompt_show_status 1

set VISUAL mcedit
set PATH /sitesbox/bin $PATH
set DRUSH_LAUNCHER_FALLBACK ~/.composer/vendor/bin/drush
set u (basename $PWD)
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
