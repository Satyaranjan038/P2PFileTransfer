from flask import Flask, request, jsonify
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
    sessions[session_id] = {}
    return jsonify({"url": f"https://your-backend-url.com/download/{session_id}"})


@socketio.on("offer")
def handle_offer(data):
    """
    Handles WebRTC offer from a sender and broadcasts it to the receiver.
    """
    session_id = data.get("session_id")
    if session_id in sessions:
        sessions[session_id]["offer"] = data["offer"]
        emit("offer", data, broadcast=True)


@socketio.on("answer")
def handle_answer(data):
    """
    Handles WebRTC answer from a receiver and broadcasts it to the sender.
    """
    emit("answer", data, broadcast=True)


@socketio.on("candidate")
def handle_candidate(data):
    """
    Handles ICE candidates and broadcasts them to peers.
    """
    emit("candidate", data, broadcast=True)


if __name__ == "__main__":
    import eventlet
    import eventlet.wsgi

    # Run the app using Eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 5000)), app)
