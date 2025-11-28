document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("modal");
  const openModalBtn = document.getElementById("openModalBtn");
  const closeModalBtn = document.getElementById("closeModalBtn");
  const cancelBtn = document.getElementById("cancelBtn");

  openModalBtn.addEventListener("click", () => {
    modal.style.display = "block";
  });

  closeModalBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  cancelBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });
});