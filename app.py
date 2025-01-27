from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_socketio import SocketIO, join_room, emit
from flask_cors import CORS
import os
import uuid
from io import BytesIO

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["SECRET_KEY"] = "secret!"
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage for sessions and files
sessions = {}

# Endpoint to create a new session
@app.route("/create-session", methods=["POST"])
def create_session():
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"files": {}}
    session_url = f"http://{request.host}/{session_id}"
    return jsonify({"session_id": session_id, "url": session_url})


# Endpoint to upload files
@app.route("/upload/<session_id>", methods=["POST"])
def upload_files(session_id):
    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404

    files = request.files.getlist("files")
    for file in files:
        sessions[session_id]["files"][file.filename] = file.read()

    return jsonify({"message": "Files uploaded successfully"})


# Endpoint to list files
@app.route("/files/<session_id>", methods=["GET"])
def list_files(session_id):
    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404

    file_list = list(sessions[session_id]["files"].keys())
    return jsonify({"files": file_list})


# Endpoint to download a specific file
@app.route("/download/<session_id>/<filename>", methods=["GET"])
def download_file(session_id, filename):
    if session_id not in sessions or filename not in sessions[session_id]["files"]:
        return jsonify({"error": "File not found"}), 404

    file_data = sessions[session_id]["files"][filename]
    return send_file(BytesIO(file_data), download_name=filename, as_attachment=True)


# Serve the frontend for /ui route
@app.route("/ui")
def serve_frontend():
    return send_from_directory("static", "index.html")


# Serve session frontend (for specific session URL)
@app.route("/<session_id>")
def serve_session_frontend(session_id):
    if session_id in sessions:
        return send_from_directory("static", "download.html")
    else:
        return jsonify({"error": "Session not found"}), 404


# WebSocket signaling for P2P communication
@socketio.on("join")
def handle_join(data):
    session_id = data.get("session_id")
    if session_id in sessions:
        join_room(session_id)
        emit("joined", {"message": f"User joined session {session_id}"}, to=session_id)


@socketio.on("signal")
def handle_signal(data):
    session_id = data.get("session_id")
    signal_data = data.get("signal")
    emit("signal", signal_data, to=session_id, include_self=False)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)

