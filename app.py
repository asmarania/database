from flask import Flask, request
import os
import json
import paramiko

app = Flask(__name__)

def upload_to_sftp(local_path, remote_filename):
    host = os.environ.get("SFTP_HOST")
    port = 22
    username = os.environ.get("SFTP_USER")
    password = os.environ.get("SFTP_PASS")

    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    sftp.chdir("home")  # Change to the appropriate directory

    sftp.put(local_path, remote_filename)

    sftp.close()
    transport.close()

@app.route("/upload_json", methods=["POST"])
def upload_json():
    try:
        incoming = request.get_json()
        if not incoming or "data" not in incoming:
            return "❌ Invalid JSON: missing 'data' field", 400

        # Write JSON to a fixed file name
        local_filename = "/tmp/data.json"
        remote_filename = "data.json"

        with open(local_filename, "w") as f:
            json.dump(incoming["data"], f, indent=2)

        upload_to_sftp(local_filename, remote_filename)

        # Optional: Delete the local file after upload
        os.remove(local_filename)

        return f"✅ JSON uploaded and replaced as {remote_filename}"

    except Exception as e:
        return f"❌ Failed to upload JSON: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
