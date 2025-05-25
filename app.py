
from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
import uuid
import threading
import subprocess
import requests
import json
import tempfile

app = Flask(__name__)

HTML_FORM = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Streamdump</title>
</head>
<body>
  <h2>Streamdump Downloader</h2>
  <form id="form" method="POST" action="/api/submit" enctype="multipart/form-data">
    <label>Video URL:</label><br>
    <input type="text" name="url" required><br><br>

    <label>Client ID:</label><br>
    <input type="text" name="client_id" required><br><br>
    <label>Tenant ID:</label><br>
    <input type="text" name="tenant_id" required><br><br>
    <label>Client Secret:</label><br>
    <input type="text" name="client_secret" required><br><br>

    <label>Cookies JSON (.json):</label><br>
    <input type="file" name="cookies_json"><br><br>

    <label>Cookies TXT (.txt):</label><br>
    <input type="file" name="cookies_txt"><br><br>

    <label>Raw Cookie Text:</label><br>
    <textarea name="cookie_text" rows="5" cols="50"></textarea><br><br>

    <button type="submit">Submit</button>
  </form>
  <p id="status"></p>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML_FORM)

def upload_to_onedrive(file_path, file_name, client_id, client_secret, tenant_id):
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    headers = { "Content-Type": "application/x-www-form-urlencoded" }
    data = {
        "client_id": client_id,
        "scope": "https://graph.microsoft.com/.default",
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    r = requests.post(token_url, headers=headers, data=data)
    access_token = r.json()["access_token"]

    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{file_name}:/createUploadSession"
    headers = { "Authorization": f"Bearer {access_token}", "Content-Type": "application/json" }
    upload_session = requests.post(upload_url, headers=headers).json()
    upload_link = upload_session["uploadUrl"]

    chunk_size = 3276800
    file_size = os.path.getsize(file_path)

    with open(file_path, 'rb') as f:
        for i in range(0, file_size, chunk_size):
            chunk_data = f.read(chunk_size)
            start = i
            end = min(i + chunk_size - 1, file_size - 1)
            content_range = f"bytes {start}-{end}/{file_size}"
            headers = {
                "Content-Length": str(end - start + 1),
                "Content-Range": content_range
            }
            requests.put(upload_link, headers=headers, data=chunk_data)

@app.route("/api/submit", methods=["POST"])
def submit():
    url = request.form["url"]
    client_id = request.form["client_id"]
    tenant_id = request.form["tenant_id"]
    client_secret = request.form["client_secret"]

    tmp_dir = tempfile.mkdtemp()
    cookie_file_path = os.path.join(tmp_dir, "cookies.txt")

    if "cookies_json" in request.files and request.files["cookies_json"].filename:
        cookie_file = request.files["cookies_json"]
        cookie_json = json.load(cookie_file)
        with open(cookie_file_path, "w") as f:
            for c in cookie_json:
                f.write("	".join([c.get(k, "") for k in ["domain", "flag", "path", "secure", "expirationDate", "name", "value"]]) + "
")
    elif "cookies_txt" in request.files and request.files["cookies_txt"].filename:
        cookie_file = request.files["cookies_txt"]
        cookie_file.save(cookie_file_path)
    elif "cookie_text" in request.form and request.form["cookie_text"]:
        with open(cookie_file_path, "w") as f:
            f.write(request.form["cookie_text"])

    output_file = os.path.join(tmp_dir, f"{uuid.uuid4()}.mp4")
    cmd = ["yt-dlp", url, "-o", output_file]
    if os.path.exists(cookie_file_path):
        cmd.extend(["--cookies", cookie_file_path])
    subprocess.run(cmd)

    download_file = [f for f in os.listdir(tmp_dir) if f.endswith(".mp4")][0]
    final_path = os.path.join(tmp_dir, download_file)

    threading.Thread(target=upload_to_onedrive, args=(final_path, download_file, client_id, client_secret, tenant_id)).start()

    return jsonify({"status": "Download started. Will upload to OneDrive when done."})

if __name__ == "__main__":
    app.run(debug=True)
