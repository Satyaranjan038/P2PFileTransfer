const serverUrl = "https://p2pfiletransfer-r7ge.onrender.com";
const socket = io(serverUrl);

let sessionId = null;

// Step 1: Create a session
document.getElementById("createSessionButton").addEventListener("click", () => {
  fetch(`${serverUrl}/create-session`, { method: "POST" })
    .then((response) => response.json())
    .then((data) => {
      sessionId = data.session_id;
      document.getElementById("sessionUrl").textContent = `Session URL: ${data.url}`;
      document.getElementById("uploadSection").style.display = "block";
    });
});

// Step 2: Upload files
document.getElementById("uploadButton").addEventListener("click", () => {
  const fileInput = document.getElementById("fileInput");
  const files = fileInput.files;
  if (files.length === 0) {
    alert("Please select files to upload.");
    return;
  }

  const formData = new FormData();
  for (let file of files) {
    formData.append("files", file);
  }

  fetch(`${serverUrl}/upload/${sessionId}`, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("uploadStatus").textContent = data.message;
    });
});

// Step 3: Join a session and download files
socket.on("connect", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const joinSessionId = urlParams.get("session");
  if (joinSessionId) {
    sessionId = joinSessionId;
    document.getElementById("createSessionSection").style.display = "none";
    document.getElementById("uploadSection").style.display = "none";
    document.getElementById("downloadSection").style.display = "block";

    fetch(`${serverUrl}/files/${sessionId}`)
      .then((response) => response.json())
      .then((data) => {
        const fileList = document.getElementById("fileList");
        data.files.forEach((file) => {
          const listItem = document.createElement("li");
          listItem.textContent = file;

          const downloadButton = document.createElement("button");
          downloadButton.textContent = "Download";
          downloadButton.addEventListener("click", () => downloadFile(file));

          listItem.appendChild(downloadButton);
          fileList.appendChild(listItem);
        });
      });

    socket.emit("join", { session_id: sessionId });
  }
});

function downloadFile(filename) {
  const link = document.createElement("a");
  link.href = `${serverUrl}/download/${sessionId}/${filename}`;
  link.download = filename;
  link.click();
}
