document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("modal");
  const openBtn = document.getElementById("openModalBtn");
  const closeBtn = document.getElementById("closeModalBtn");

  // ===== Відкрити / закрити модальне вікно =====
  openBtn.addEventListener("click", () => {
    modal.style.display = "block";
  });

  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  window.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });

  // ===== Показ повідомлення після натискання кнопки "Додати техніку" =====
  const form = modal.querySelector("form");

  form.addEventListener("submit", function () {
    showMessage("Техніку додано успішно!");
  });

  // ===== Функція для показу повідомлень =====
  function showMessage(text) {
    const msg = document.createElement("div");
    msg.classList.add("toast-message");
    msg.textContent = text;
    document.body.appendChild(msg);

    // Плавна поява
    setTimeout(() => msg.classList.add("show"), 50);

    // Автоматичне зникнення
    setTimeout(() => {
      msg.classList.remove("show");
      setTimeout(() => msg.remove(), 400);
    }, 3000);
  }
});
