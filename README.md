## config

```json
{
  "repo_url": "https://gitlab.com/example-user/my-repo",
  "branch": "main",
  "access_token": "glpat-xxxxxxxxxxxxxxxx",
  "output_name": "myproject.tar"
}
```

## build
```shell
pyinstaller --onefile --add-data "templates:templates" app.py
```

## run
```shell
CONFIG_PATH=config/download_config.json ./dist/app
```
