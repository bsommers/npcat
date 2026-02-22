import os
import uuid
import shutil
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "/tmp/netcap_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/api/capture", methods=["POST"])
def capture():
    data = request.json
    interface = data.get("interface")
    count = data.get("count")
    filter_expr = data.get("filter", "")
    duration = data.get("duration", 10)

    filename = f"{uuid.uuid4()}.pcap"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    cmd = ["netcapanalysis", "capture", "-o", filepath, "-d", str(duration)]

    if interface:
        cmd.extend(["-i", interface])
    if count:
        cmd.extend(["-c", str(count)])
    if filter_expr:
        cmd.extend(["-f", filter_expr])

    try:
        timeout = duration + 10 if duration else 60
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 400

        return jsonify(
            {
                "filename": filename,
                "filepath": filepath,
                "message": "Capture completed",
                "duration": duration,
            }
        )
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Capture timed out"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload", methods=["POST"])
def upload_pcap():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith((".pcap", ".pcapng", ".cap")):
        return jsonify({"error": "Invalid file type"}), 400

    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    return jsonify(
        {"filename": file.filename, "saved_as": filename, "filepath": filepath}
    )


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.json
    filepath = data.get("filepath")

    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 400

    output_file = f"/tmp/netcap_{uuid.uuid4()}.md"

    try:
        result = subprocess.run(
            [
                "netcapanalysis",
                "analyze",
                "-i",
                filepath,
                "-o",
                output_file,
                "--no-png",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 400

        with open(output_file, "r") as f:
            report_content = f.read()

        os.remove(output_file)

        return jsonify({"report": report_content, "filepath": filepath})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/timeline", methods=["POST"])
def timeline():
    data = request.json
    filepaths = data.get("filepaths", [])

    if not filepaths:
        return jsonify({"error": "No files provided"}), 400

    for fp in filepaths:
        if not os.path.exists(fp):
            return jsonify({"error": f"File not found: {fp}"}), 400

    output_file = f"/tmp/netcap_{uuid.uuid4()}.md"

    try:
        cmd = ["netcapanalysis", "timeline", "-o", output_file, "--no-png"]
        for fp in filepaths:
            cmd.extend(["-i", fp])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 400

        with open(output_file, "r") as f:
            report_content = f.read()

        os.remove(output_file)

        return jsonify({"report": report_content, "filepaths": filepaths})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chart", methods=["POST"])
def chart():
    data = request.json
    filepath = data.get("filepath")
    chart_type = data.get("type", "port")

    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 400

    filename = f"{uuid.uuid4()}.png"
    output_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        result = subprocess.run(
            [
                "netcapanalysis",
                "chart",
                "-i",
                filepath,
                "-o",
                output_path,
                "-t",
                chart_type,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 400

        return send_file(output_path, mimetype="image/png")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/files", methods=["GET"])
def list_files():
    files = []
    for f in os.listdir(UPLOAD_FOLDER):
        if f.endswith((".pcap", ".pcapng", ".cap")):
            filepath = os.path.join(UPLOAD_FOLDER, f)
            files.append(
                {
                    "name": f,
                    "size": os.path.getsize(filepath),
                    "modified": os.path.getmtime(filepath),
                }
            )
    return jsonify({"files": files})


@app.route("/api/files/<path:filename>", methods=["DELETE"])
def delete_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"message": "Deleted"})
    return jsonify({"error": "File not found"}), 404


@app.route("/api/interfaces", methods=["GET"])
def interfaces():
    try:
        from scapy.all import get_if_list

        ifs = get_if_list()
        return jsonify({"interfaces": ifs})
    except Exception as e:
        return jsonify({"error": str(e), "interfaces": ["eth0", "wlan0", "lo"]})


@app.route("/api/version", methods=["GET"])
def version():
    return jsonify({"version": "1.0.0"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
