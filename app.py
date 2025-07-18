import os
import json
import requests
import gzip
import tarfile
import tempfile
from io import BytesIO
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
CONFIG_PATH = "config/download_config.json"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

tar_file_name = None  # 생성된 .tar 파일 이름

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def download_and_convert(config):
    global tar_file_name

    repo_url = config["repo_url"].rstrip("/")
    branch = config["branch"]
    token = config["access_token"]
    output_name = config["output_name"].strip()
    tar_file_name = output_name

    repo_name = repo_url.split("/")[-1]
    archive_url = f"{repo_url}/-/archive/{branch}/{repo_name}-{branch}.tar.gz"
    print(f"[INFO] archive_url: {archive_url}")

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(archive_url, headers=headers, stream=True)
    if response.status_code != 200 or "html" in response.headers.get("Content-Type", ""):
        print("❌ 다운로드 실패")
        print(response.status_code, response.headers.get("Content-Type"))
        print(response.text[:500])
        return

    tar_gz_bytes = BytesIO(response.content)
    with gzip.GzipFile(fileobj=tar_gz_bytes) as gz:
        with tempfile.NamedTemporaryFile(delete=False) as temp_tar_file:
            temp_tar_file.write(gz.read())
            temp_tar_path = temp_tar_file.name

    tar_path = os.path.join(DOWNLOAD_DIR, output_name)
    new_root = os.path.splitext(output_name)[0]

    with tarfile.open(temp_tar_path, "r") as old_tar:
        with tarfile.open(tar_path, "w", format=tarfile.GNU_FORMAT) as new_tar:
            for member in old_tar.getmembers():
                parts = member.name.split("/")
                if len(parts) < 2:
                    continue
                rest_path = "/".join(parts[1:])
                member.name = f"{new_root}/{rest_path}" if rest_path else new_root
                file_data = old_tar.extractfile(member) if member.isfile() else None
                new_tar.addfile(member, file_data)

    os.remove(temp_tar_path)
    print(f"✅ 변환 완료: {tar_path}")

@app.route("/")
def index():
    return render_template("index.html", filename=tar_file_name)

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    config = load_config()
    download_and_convert(config)
    app.run(debug=True, host="0.0.0.0", port=5000)
