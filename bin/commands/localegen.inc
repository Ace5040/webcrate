function Localegen() {
	mkdir -p ./locale
	xgettext -o ./locale/webcrate.pot -L Shell --keyword=t --from-code=UTF-8 \
		./bin/webcrate \
		./bin/commands/configure.inc \
		./bin/commands/help.inc \
		./bin/commands/start.inc \
		./bin/commands/stop.inc \
		./bin/commands/build.inc \
		./bin/commands/dock.inc \
		./bin/commands/push.inc \
		./bin/commands/backup.inc \
		./bin/includes/generate-config.inc \
		./bin/includes/init.inc \
		./bin/includes/projects.inc \
		./bin/includes/services.inc
	if [[ ! -f "./locale/webcrate-ru.po" ]] ; then
		msginit --no-translator -i ./locale/webcrate.pot -o ./locale/webcrate-ru.po -l ru_RU.UTF-8
	else
		msgmerge -NU ./locale/webcrate-ru.po ./locale/webcrate.pot
	fi
	if [[ ! -f "./locale/webcrate-zh.po" ]] ; then
		msginit --no-translator -i ./locale/webcrate.pot -o ./locale/webcrate-zh.po -l zh_CN.UTF-8
	else
		msgmerge -NU ./locale/webcrate-zh.po ./locale/webcrate.pot
	fi
	mkdir -p ./locale/ru/LC_MESSAGES
	msgfmt ./locale/webcrate-ru.po -o ./locale/ru/LC_MESSAGES/webcrate.mo
	mkdir -p ./locale/zh/LC_MESSAGES
	msgfmt ./locale/webcrate-zh.po -o ./locale/zh/LC_MESSAGES/webcrate.mo
}
