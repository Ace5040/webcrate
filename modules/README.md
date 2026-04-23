# Webcrate Modules

Each subdirectory here is a module. Modules are automatically discovered at startup.

## Directory structure

```
modules/
  core/          # Built-in backend runtimes (PHP versions, Gunicorn)
    php84/
      module.yml
    gunicorn/
      module.yml
  services/      # Built-in service containers (databases, cache, search)
    mysql/
      module.yml
    memcached/
      module.yml
  my-worker/     # Example: user-defined custom module (any subfolder at any depth)
    module.yml
```

## Adding a custom module

Create a folder with a `module.yml` anywhere inside `modules/`:

```
modules/
  custom/
    redis/
      module.yml
```

### module.yml for a custom Docker image

```yaml
type: custom
category: custom      # backend | database | cache | search | custom
label: "Redis 7"
image: "redis:7"
# Optional:
command: "redis-server --appendonly yes"
restart: "unless-stopped"
env:
  MY_VAR: value
volumes:
  - host: data/redis   # relative to project folder, or absolute path
    container: /data
```

### module.yml fields

| Field            | Required | Description |
|-----------------|----------|-------------|
| `type`          | yes      | `core`, `mysql`, `mysql5`, `postgresql`, `memcached`, `solr`, `elastic`, `custom` |
| `category`      | yes      | `backend`, `database`, `cache`, `search`, `custom` |
| `label`         | yes      | Display name shown in admin panel |
| `image`         | custom   | Docker image (required for `custom` type) |
| `command`       | no       | Override container command |
| `restart`       | no       | Restart policy (default: `unless-stopped`) |
| `env`           | no       | Environment variables map |
| `volumes`       | no       | List of `{host, container}` volume mounts |
| `backend_name`  | core     | Used by core modules: `php` or `gunicorn` |
| `backend_version` | core   | Used by core modules: `84`, `83`, ..., `latest` |
