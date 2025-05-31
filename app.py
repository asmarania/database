from flask import Flask, request
import os
import json
import paramiko
import datetime

app = Flask(__name__)

def upload_to_sftp(local_path, remote_filename):
    host = os.environ.get("SFTP_HOST")
    port = 22
    username = os.environ.get("SFTP_USER")
    password = os.environ.get("SFTP_PASS")

    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    sftp.chdir("home")  # Change to home dir

    sftp.put(local_path, remote_filename)

    sftp.close()
    transport.close()

@app.route("/upload_json", methods=["POST"])
def upload_json():
    try:
        data = request.get_json()
        if not data:
            return "No JSON received", 400

        # Create JSON file locally with timestamp in filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        local_filename = f"/tmp/data_{timestamp}.json"
        with open(local_filename, "w") as f:
            json.dump(data, f, indent=2)

        # Upload to SFTP with same filename under home
        remote_filename = f"data_{timestamp}.json"
        upload_to_sftp(local_filename, remote_filename)

        return f"✅ JSON uploaded as {remote_filename}"

    except Exception as e:
        return f"❌ Failed to upload JSON: {str(e)}", 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
