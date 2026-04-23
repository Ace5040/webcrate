function Build() {

	BUILDTARGET=$1

	# Collect module build targets: any module folder containing a Dockerfile
	_module_targets=()
	while IFS= read -r -d '' dockerfile; do
		module_dir=$(dirname "$dockerfile")
		module_name=$(basename "$module_dir")
		_module_targets+=("$module_name")
	done < <(find "$WEBCRATE_PWD/modules" -name "Dockerfile" -print0 2>/dev/null)

	# Known system targets (non-module)
	_system_targets=(all nginx utils-pwgen utils-docker admin dnsmasq stats)

	# Validate target
	_target_valid=false
	for t in "${_system_targets[@]}" "${_module_targets[@]}"; do
		[ "$BUILDTARGET" = "$t" ] && _target_valid=true && break
	done
	# 'core' is an alias for all core modules
	[ "$BUILDTARGET" = "core" ] && _target_valid=true

	if [ "$_target_valid" = "false" ]; then
		_all_targets="all, nginx, utils-pwgen, utils-docker, core, admin, stats"
		for t in "${_module_targets[@]}"; do _all_targets="$_all_targets, $t"; done
		echo "$(printf "$(t "Unknown build target: '%s'. Use one of: %s")" "$BUILDTARGET" "$_all_targets")"
		exit 1
	fi

	LONGOPTS=no-cache,update-base-images,progress-plain
	OPTIONS=nup
	PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@") || exit 2
	eval set -- "$PARSED"
	BUILD_OPTIONS=''
	u=n
	while true; do
		case "$1" in
			-n|--no-cache)
				BUILD_OPTIONS=$BUILD_OPTIONS' --no-cache'
				shift
				;;
			-u|--update-base-images)
				u=y
				shift
				;;
			-p|--progress-plain)
				BUILD_OPTIONS=$BUILD_OPTIONS' --progress=plain'
				shift
				;;
			--)
				shift
				break
				;;
			*)
				echo "$(t "Programming error")"
				exit 3
				;;
		esac
	done
	if [ $# -eq 1 ]
	then
		if [ "$u" = "y" ]
		then
			docker pull $IMAGE_ALPINE_BASE
			docker pull $IMAGE_DEBIAN_STABLE_SLIM
			docker pull $IMAGE_DEBIAN_SLIM
			docker pull $IMAGE_NGINX_BASE
		fi
	else
		echo "$(t "Wrong number of args")"
		exit 4
	fi

	# ── System service builds ────────────────────────────────────────────────
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "nginx" ]; then
		docker build -t $IMAGE_NGINX --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_NGINX_BASE $WEBCRATE_PWD/src/nginx $BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "dnsmasq" ]; then
		docker build -t $IMAGE_DNSMASQ --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_ALPINE_BASE $WEBCRATE_PWD/src/dnsmasq $BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "utils-pwgen" ]; then
		docker build -t $IMAGE_UTILS_PWGEN --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_ALPINE_BASE $WEBCRATE_PWD/src/utils-pwgen $BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "utils-docker" ]; then
		docker build -t $IMAGE_UTILS_DOCKER --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_ALPINE_BASE $WEBCRATE_PWD/src/utils-docker $BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "admin" ]; then
		docker build -t $IMAGE_ADMIN --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_DEBIAN_STABLE_SLIM $WEBCRATE_PWD/src/admin $BUILD_OPTIONS
	fi
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "stats" ]; then
		docker build -t $IMAGE_STATS --build-context src=$WEBCRATE_PWD/src --build-arg IMAGE=$IMAGE_DEBIAN_STABLE_SLIM $WEBCRATE_PWD/src/stats $BUILD_OPTIONS
	fi

	# ── Module builds: discovered from modules/ subdirectories ───────────────
	# Each module with a Dockerfile and an image field in module.yml is buildable.
	# build_image_var in module.yml points to an images.default variable name;
	# if absent, fall back to the 'image' field directly.
	_build_module() {
		local module_dir="$1"
		local module_name
		module_name=$(basename "$module_dir")

		local module_yml="$module_dir/module.yml"
		[ -f "$module_yml" ] || return

		# Read image tag from module.yml (image field)
		local image_tag
		image_tag=$(python3 -c "
import yaml, sys
with open('$module_yml') as f:
    d = yaml.safe_load(f)
print(d.get('image', ''))
" 2>/dev/null)
		[ -z "$image_tag" ] && { echo "Module $module_name: no 'image' in module.yml, skipping"; return; }

		# Read base image variable name (base_image_var) from module.yml, default to IMAGE_DEBIAN_STABLE_SLIM
		local base_image_var
		base_image_var=$(python3 -c "
import yaml, sys
with open('$module_yml') as f:
    d = yaml.safe_load(f)
print(d.get('base_image_var', 'IMAGE_DEBIAN_STABLE_SLIM'))
" 2>/dev/null)

		# Resolve base image value from environment
		local base_image="${!base_image_var}"
		[ -z "$base_image" ] && base_image="$IMAGE_DEBIAN_STABLE_SLIM"

		echo "Building module '$module_name' → $image_tag (base: $base_image)"
		docker build -t "$image_tag" \
			--build-context src=$WEBCRATE_PWD/src \
			--build-arg IMAGE="$base_image" \
			"$module_dir" $BUILD_OPTIONS
	}

	# Build 'core' alias = all core-category modules
	if [ "$BUILDTARGET" = "all" ] || [ "$BUILDTARGET" = "core" ]; then
		while IFS= read -r -d '' dockerfile; do
			module_dir=$(dirname "$dockerfile")
			_build_module "$module_dir"
		done < <(find "$WEBCRATE_PWD/modules/core" -name "Dockerfile" -print0 2>/dev/null)
	fi

	# Build a single named module target (e.g. 'php84', 'gunicorn', 'nginx')
	if [[ ! " all core ${_system_targets[*]} " =~ " $BUILDTARGET " ]]; then
		while IFS= read -r -d '' dockerfile; do
			module_dir=$(dirname "$dockerfile")
			module_name=$(basename "$module_dir")
			if [ "$module_name" = "$BUILDTARGET" ]; then
				_build_module "$module_dir"
			fi
		done < <(find "$WEBCRATE_PWD/modules" -name "Dockerfile" -print0 2>/dev/null)
	fi

}
