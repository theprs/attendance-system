const video = document.getElementById("webcam");
const captureBtn = document.getElementById("captureBtn");
const result = document.getElementById("result");

// Start webcam
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
  });

// Capture image & send to backend
captureBtn.addEventListener("click", async () => {
  // Create canvas and draw current frame
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Convert to blob
  canvas.toBlob(async blob => {
    const formData = new FormData();
    formData.append("file", blob, "capture.jpg");

    try {
      const response = await fetch("http://localhost:8000/recognize_face/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (response.ok) {
        result.textContent = `✅ Attendance marked for: ${data.name}`;
      } else {
        result.textContent = `❌ ${data.error}`;
      }
    } catch (err) {
      result.textContent = "⚠️ Error connecting to backend.";
    }
  }, "image/jpeg");
});
