import sys
import os
import json
import requests
import gzip
import tarfile
import tempfile
from io import BytesIO
from flask import Flask, render_template, send_file

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

TEMPLATE_PATH = resource_path("templates")
app = Flask(__name__, template_folder=TEMPLATE_PATH)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
CONFIG_PATH = os.environ.get("CONFIG_PATH", os.path.join("config", "download_config.json"))
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

tar_file_name = None  # 생성된 .tar 파일 이름

def load_config():
    with open(CONFIG_PATH) as f:
        config = json.load(f)

        global tar_file_name

        output_name = config["output_name"].strip()
        tar_file_name = output_name

        return config

def download_tar(config):
    global tar_file_name

    repo_url = config["repo_url"].rstrip("/")
    branch = config["branch"]
    token = config["access_token"]
    output_name = config["output_name"].strip()
    tar_file_name = output_name

    repo_name = repo_url.split("/")[-1]
    archive_url = f"{repo_url}/-/archive/{branch}/{repo_name}-{branch}.tar"
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

    new_top_dir = os.path.splitext(output_name)[0]
    tar_path = os.path.join(DOWNLOAD_DIR, output_name)

    source_tar = BytesIO(response.content)
    repackaged_tar = BytesIO()

    with tarfile.open(fileobj=source_tar, mode="r") as old_tar:
        with tarfile.open(fileobj=repackaged_tar, mode="w", format=tarfile.GNU_FORMAT) as new_tar:
            for member in old_tar.getmembers():
                parts = member.name.split("/")
                if len(parts) > 0:
                    parts[0] = new_top_dir
                member.name = "/".join(parts)
                file_data = old_tar.extractfile(member) if member.isfile() else None
                new_tar.addfile(member, file_data)

    with open(tar_path, "wb") as f:
        f.write(repackaged_tar.getbuffer())

    print(f"[INFO] Saved repackaged tar to {tar_path}")
    return output_name

@app.route("/")
def index():
    return render_template("index.html", filename=tar_file_name)

@app.route("/download/<filename>")
def download(filename):
    config = load_config()
    try:
        download_tar(config)
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        if not os.path.exists(file_path):
            return f"❌ 파일이 존재하지 않습니다: {file_path}", 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"❌ 다운로드 실패: {str(e)}", 500
    except Exception as e:
        return f"❌ 다운로드 실패: {str(e)}", 500

if __name__ == "__main__":
    load_config()
    app.run(debug=True, host="0.0.0.0", port=5000)
