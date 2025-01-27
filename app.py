from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable WebSocket support

# Store session data in memory
sessions = {}


@app.route("/generate-url", methods=["POST"])
def generate_url():
    """
    Generates a unique URL for initiating a session.
    """
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"file_data": None, "filename": None}
    return jsonify({"url": f"http://{request.host}/download/{session_id}"})


@app.route("/upload/<session_id>", methods=["POST"])
def upload_file(session_id):
    """
    Handles the file upload and stores it in memory for the session.
    """
    if session_id not in sessions:
        return jsonify({"error": "Invalid session ID"}), 404

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    sessions[session_id]["file_data"] = file.read()
    sessions[session_id]["filename"] = file.filename

    return jsonify({"message": "File uploaded successfully"})


@app.route("/download/<session_id>", methods=["GET"])
def download_file(session_id):
    """
    Handles the file download request for a specific session.
    """
    session_data = sessions.get(session_id)
    if not session_data or not session_data.get("file_data"):
        return jsonify({"error": "Session not found or no file uploaded"}), 404

    file_data = session_data["file_data"]
    filename = session_data["filename"]

    # Stream the file to the client
    return Response(
        file_data,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/octet-stream",
        },
    )


if __name__ == "__main__":
    import eventlet
    import eventlet.wsgi

    # Run the app using Eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 5000)), app)
