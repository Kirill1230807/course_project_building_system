document.addEventListener("DOMContentLoaded", () => {
  // ==== Таби ====
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(btn.dataset.tab).classList.add("active");
    });
  });

  // ==== Модальні ====
  const modals = [
    {open: "#openMaterialModal", modal: "#materialModal", close: "#closeMaterialModal"},
    {open: "#openSupplierModal", modal: "#supplierModal", close: "#closeSupplierModal"},
  ];

  modals.forEach(({open, modal, close}) => {
    const openBtn = document.querySelector(open);
    const modalEl = document.querySelector(modal);
    const closeBtn = document.querySelector(close);

    if (openBtn && modalEl && closeBtn) {
      openBtn.onclick = () => modalEl.style.display = "block";
      closeBtn.onclick = () => modalEl.style.display = "none";
      window.onclick = e => { if (e.target === modalEl) modalEl.style.display = "none"; };
    }
  });
});
