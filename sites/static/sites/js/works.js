// Відкриття/закриття модального вікна
const modal = document.getElementById("modal");
const openModalBtn = document.getElementById("openModalBtn");
const closeModalBtn = document.getElementById("closeModalBtn");

openModalBtn.onclick = () => modal.style.display = "block";
closeModalBtn.onclick = () => modal.style.display = "none";
window.onclick = e => { if (e.target === modal) modal.style.display = "none"; };
