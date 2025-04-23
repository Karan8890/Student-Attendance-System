const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const resultMessage = document.getElementById("result-message");
const attendanceList = document.getElementById("attendance-list");

// Start camera
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
  })
  .catch(error => {
    console.error("Camera access denied", error);
  });

// Define capture function
function capture() {
  const context = canvas.getContext("2d");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  const imageData = canvas.toDataURL("image/jpeg");

  fetch('/mark_attendance', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: imageData })
  })
  
  .then(response => response.text())
  .then(data => {
    resultMessage.textContent = data;
    loadRecentAttendance();
  })
  .catch(error => {
    console.error("Error:", error);
    resultMessage.textContent = "❌ Error marking attendance";
  });
}

function loadRecentAttendance() {
  fetch('/recent_attendance')
    .then(res => res.json())
    .then(data => {
      attendanceList.innerHTML = '';
      data.forEach(entry => {
        const li = document.createElement('li');
        li.textContent = `${entry.name} - ${entry.time}`;
        attendanceList.appendChild(li);
      });
    });
}
