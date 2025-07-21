# config (config/download_config.json)
```json
{
  "repo_url": "https://gitlab.com/example-user/my-repo",
  "branch": "main",
  "access_token": "glpat-xxxxxxxxxxxxxxxx",
  "output_name": "myproject.tar"
}
```

# 로컬 실행
```
# 가상환경 설치 (옵션)
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install flask requests

# 실행
python app.py
```

# 패키징 및 실행 (리눅스)
```
pip install pyinstaller

pyinstaller --onefile --add-data "templates:templates" app.py

CONFIG_PATH=config/download_config.json ./dist/app
```
