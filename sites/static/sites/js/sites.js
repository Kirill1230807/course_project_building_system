document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("modal");
    const openBtn = document.getElementById("openModalBtn");
    const closeBtn = document.getElementById("closeModalBtn");
    const buttons = document.querySelectorAll(".tab-button");
    const tabs = document.querySelectorAll(".tab-content");

    if (openBtn) openBtn.onclick = () => modal.style.display = "flex";
    if (closeBtn) closeBtn.onclick = () => modal.style.display = "none";

    window.onclick = (e) => {
        if (e.target === modal) modal.style.display = "none";
    };

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {

            buttons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const tab = btn.dataset.tab;
            const targetId = "tab-" + tab;

            tabs.forEach(t => {
                if (t.id === targetId) {
                    t.classList.add("active");
                    t.style.display = "block";
                } else {
                    t.classList.remove("active");
                    t.style.display = "none";
                }
            });
        });
    });
});
