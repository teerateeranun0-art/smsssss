# web/RUN-WEB.py
from flask import Flask, render_template, request, jsonify
import subprocess
import threading
import os
import sys
import webbrowser
import time

app = Flask(__name__)

output_logs = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRAM_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "program"))

def get_script_path(mode):
    if mode == "fast":
        filename = "SMS-Fast.py"
    elif mode == "super":
        filename = "SMS-Super.py"
    else:
        filename = "SMS-Slow.py"
    return os.path.join(PROGRAM_DIR, filename)

def run_script(script_path, phone, count):
    global output_logs
    try:
        output_logs.clear()
        output_logs.append(f"[*] start: {script_path}")
        output_logs.append(f"[*] target phone: {phone}, count: {count}")

        process = subprocess.Popen(
            [sys.executable, "-u", script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=PROGRAM_DIR
        )

        try:
            input_str = f"{phone}\n{count}\n"
            process.stdin.write(input_str)
            process.stdin.flush()
        except Exception as e:
            output_logs.append(f"[!] Error sending input: {e}")

        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                output_logs.append(line.strip())

        stderr = process.stderr.read()
        if stderr:
            output_logs.append(f"[!] Error: {stderr}")

        output_logs.append("[*] Script finished.")

    except Exception as e:
        output_logs.append(f"[!] System Error: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run():
    data = request.json
    phone = data.get("phone")
    count = data.get("count")
    mode = data.get("mode")

    if not phone or not count:
        return jsonify({"status": "error", "message": "Please fill in all fields!"})

    script_path = get_script_path(mode)

    if not os.path.exists(script_path):
        return jsonify({"status": "error", "message": f"File not found: {script_path} \n(Please check if the file exists in the program folder)"})

    threading.Thread(target=run_script, args=(script_path, phone, count)).start()

    return jsonify({"status": "success", "message": f"Started {mode.upper()} mode!"})

@app.route("/get_logs")
def get_logs():
    return jsonify(output_logs)

def open_browser():
    url = "http://127.0.0.1:8080"
    if "ANDROID_ROOT" in os.environ:
        try:
            subprocess.run(["termux-open-url", url])
            print(f"[*] Opening web interface in Termux: {url}")
        except FileNotFoundError:
            print("[!] Command not found: termux-open-url (try running: pkg install termux-tools)")
    else:
        webbrowser.open(url)
        print(f"[*] Opening web interface: {url}")

if __name__ == "__main__":
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        threading.Timer(0.1, open_browser).start()
    app.run(host="0.0.0.0", port=8080, debug=True)
