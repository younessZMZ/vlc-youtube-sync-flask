import socket
import subprocess
import atexit
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

vlc_process = None


def send_command_to_vlc(command: str) -> None:
    """Send a command to VLC via its remote control interface."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 4212))
    sock.sendall((command + "\n").encode())
    sock.close()


def play_video() -> None:
    """
    Play the video.

    If VLC is not running, start it and play the video.
    If VLC is running, send a 'pause' command which toggles play/pause.
    """
    global vlc_process
    if vlc_process is None or vlc_process.poll() is not None:
        command = [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            "--extraintf",
            "rc",
            "--rc-host",
            "localhost:4212",
            r"C:\Users\admin\Music\HangMassive.mp3",
        ]
        vlc_process = subprocess.Popen(command)
    else:
        send_command_to_vlc("pause")


def pause_video() -> None:
    """
    Pause the video.

    Send a 'pause' command to VLC to toggle play/pause.
    """
    if vlc_process is not None:
        send_command_to_vlc("pause")


def stop_video() -> None:
    """
    Stop the video.

    Terminate the VLC process.
    """
    global vlc_process
    if vlc_process:
        vlc_process.terminate()
        vlc_process = None


@app.route("/playpause", methods=["POST"])
def playpause() -> tuple:
    """
    Handle play/pause requests.

    Expect a JSON request body with a 'command' field, which should be 'play' or 'pause'.
    """
    data = request.get_json()
    if not data:
        return jsonify({"status": "success"}), 200
    if data["command"] == "play":
        play_video()
    elif data["command"] == "pause":
        pause_video()
    else:
        return jsonify({"error": "Invalid command"}), 400

    return jsonify({"status": "success"}), 200


# Register stop_video to be called when the app is about to exit
atexit.register(stop_video)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
