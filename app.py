from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import uuid

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store session data in memory
sessions = {}


@app.route("/generate-url", methods=["POST"])
def generate_url():
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"files": {}, "closed": False}
    return jsonify({"url": f"http://{request.host}/download/{session_id}"})


@app.route("/upload/<session_id>", methods=["POST"])
def upload_file(session_id):
    if session_id not in sessions or sessions[session_id].get("closed"):
        return jsonify({"error": "Session not found or closed"}), 404

    if "files" not in request.files:
        return jsonify({"error": "No files provided"}), 400

    uploaded_files = request.files.getlist("files")
    for file in uploaded_files:
        sessions[session_id]["files"][file.filename] = file.read()

    return jsonify({"message": "Files uploaded successfully"})


@app.route("/download/<session_id>/<filename>", methods=["GET"])
def download_file(session_id, filename):
    if session_id not in sessions or sessions[session_id].get("closed"):
        return jsonify({"error": "Session not found or closed"}), 404

    file_data = sessions[session_id]["files"].get(filename)
    if not file_data:
        return jsonify({"error": "File not found"}), 404

    return Response(
        file_data,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/octet-stream",
        },
    )


@app.route("/close-session/<session_id>", methods=["POST"])
def close_session(session_id):
    if session_id in sessions:
        sessions[session_id]["closed"] = True
        return jsonify({"message": "Session closed"})
    return jsonify({"error": "Session not found"}), 404


@socketio.on("stop_transfer")
def stop_transfer(data):
    session_id = data.get("session_id")
    if session_id in sessions:
        sessions[session_id]["files"].clear()
        emit("transfer_stopped", {"message": "File transfer stopped"}, broadcast=True)


if __name__ == "__main__":
    import eventlet
    import eventlet.wsgi

    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 5000)), app)