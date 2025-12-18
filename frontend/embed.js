const embedBtn = document.getElementById("embedBtn");
const fileInput = document.getElementById("embedImage");

const downloadSection = document.getElementById("downloadSection");
const downloadBtn = document.getElementById("downloadBtn");

let signedImageUrl = null;

embedBtn.addEventListener("click", async () => {
  if (!fileInput.files.length) {
    alert("Please select an image");
    return;
  }

  embedBtn.disabled = true;
  embedBtn.textContent = "Generating...";

  const formData = new FormData();
  formData.append("image", fileInput.files[0]);

  try {
    const response = await fetch(
      "https://truorigin-backend.onrender.com/embed",
      {
        method: "POST",
        body: formData
      }
    );

    if (!response.ok) {
      throw new Error("Failed to generate AI-signed image");
    }

    const blob = await response.blob();
    signedImageUrl = URL.createObjectURL(blob);

    downloadSection.classList.remove("hidden");

  } catch (err) {
    alert("Error generating AI-signed image");
    console.error(err);
  } finally {
    embedBtn.disabled = false;
    embedBtn.textContent = "Generate AI-Signed Image";
  }
});

/* Download button */
downloadBtn.addEventListener("click", () => {
  if (!signedImageUrl) return;

  const a = document.createElement("a");
  a.href = signedImageUrl;
  a.download = "ai_signed_image";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
});
