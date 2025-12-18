const form = document.getElementById("verifyForm");
const resultDiv = document.getElementById("result");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const imageInput = document.getElementById("imageInput");
  const contextSelect = document.getElementById("contextSelect");

  const formData = new FormData();
  formData.append("image", imageInput.files[0]);
  formData.append("context", contextSelect.value);

  const response = await fetch("http://127.0.0.1:5000/verify", {
    method: "POST",
    body: formData
  });

  const data = await response.json();

  document.getElementById("status").innerText = data.detection_status;
  document.getElementById("confidence").innerText = data.confidence;
  document.getElementById("decision").innerText = data.decision;
  document.getElementById("reason").innerText = data.reason;

  const decisionEl = document.getElementById("decision");
  decisionEl.className = "";

  if (data.decision === "ALLOW") decisionEl.classList.add("allow");
  if (data.decision === "WARN") decisionEl.classList.add("warn");
  if (data.decision === "BLOCK") decisionEl.classList.add("block");

  resultDiv.classList.remove("hidden");
});
