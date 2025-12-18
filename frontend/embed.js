const btn = document.getElementById("embedBtn");

btn.addEventListener("click", async () => {
  const fileInput = document.getElementById("embedImage");

  if (!fileInput.files.length) {
    alert("Please select an image");
    return;
  }

  const formData = new FormData();
  formData.append("image", fileInput.files[0]);

  const response = await fetch("http://127.0.0.1:5000/embed", {
    method: "POST",
    body: formData
  });

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);

  const link = document.getElementById("downloadLink");
  link.href = url;
  link.textContent = "Download AI-Signed Image";

  document.getElementById("downloadSection").classList.remove("hidden");
});
