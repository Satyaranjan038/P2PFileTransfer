const socket = io("http://localhost:5000");

let selectedFiles = [];

// Fetch the list of available files
async function fetchFiles() {
    const sessionId = window.location.pathname.split("/")[1];
    const response = await fetch(`http://localhost:5000/files/${sessionId}`);
    const data = await response.json();
    if (data.files) {
        const fileList = document.getElementById("fileList");
        fileList.innerHTML = "";
        data.files.forEach((filename) => {
            const li = document.createElement("li");
            li.innerHTML = `<input type="checkbox" value="${filename}" /> ${filename}`;
            fileList.appendChild(li);
        });
    }
}

// Handle file selection
document.addEventListener("DOMContentLoaded", () => {
    const fileList = document.getElementById("fileList");
    const selectAll = document.getElementById("selectAll");
    
    if (fileList) {
        fileList.addEventListener("change", (event) => {
            const checkbox = event.target;
            const filename = checkbox.value;

            if (checkbox.checked) {
                selectedFiles.push(filename);
            } else {
                selectedFiles = selectedFiles.filter((file) => file !== filename);
            }
        });
    }

    // Handle "Select All"
    if (selectAll) {
        selectAll.addEventListener("change", () => {
            const checkboxes = document.querySelectorAll("#fileList input[type='checkbox']");
            selectedFiles = [];
            checkboxes.forEach((checkbox) => {
                checkbox.checked = selectAll.checked;
                const filename = checkbox.value;
                if (checkbox.checked) {
                    selectedFiles.push(filename);
                }
            });
        });
    }

    const downloadButton = document.getElementById("downloadButton");
    if (downloadButton) {
        downloadButton.addEventListener("click", () => {
            const sessionId = window.location.pathname.split("/")[1];

            if (selectedFiles.length > 0) {
                selectedFiles.forEach((filename) => {
                    fetch(`http://localhost:5000/download/${sessionId}/${filename}`)
                        .then((response) => response.blob())
                        .then((blob) => {
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement("a");
                            a.href = url;
                            a.download = filename;
                            a.click();
                            URL.revokeObjectURL(url);
                        })
                        .catch((error) => {
                            console.error("Error downloading file:", error);
                        });
                });
            } else {
                alert("Please select files to download.");
            }
        });
    }
});

// Socket.IO - Join room when page loads
window.onload = () => {
    const sessionId = window.location.pathname.split("/")[1];
    socket.emit("join", { session_id: sessionId });
    fetchFiles();
};
