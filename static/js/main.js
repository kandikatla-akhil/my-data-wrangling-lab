const fileUpload = document.getElementById("file-upload");
const uploadLabel = document.querySelector(".upload-label");

if (fileUpload && uploadLabel) {
  fileUpload.addEventListener("change", () => {
    const fileName = fileUpload.files.length ? fileUpload.files[0].name : "Select your dataset";
    uploadLabel.querySelector(".upload-title").textContent = fileName;
  });
}
