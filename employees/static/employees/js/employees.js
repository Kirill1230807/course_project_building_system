document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("modal");
    const openBtn = document.getElementById("openModalBtn");
    const closeBtn = document.getElementById("closeModalBtn");
    const buttons = document.querySelectorAll(".tab-button");
    const tabs = document.querySelectorAll(".tab-content");

    if (openBtn && modal) {
        openBtn.addEventListener("click", () => modal.style.display = "flex");
    }

    if (closeBtn && modal) {
        closeBtn.addEventListener("click", () => modal.style.display = "none");
    }

    window.addEventListener("click", (event) => {
        if (event.target === modal) modal.style.display = "none";
    });

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {

            buttons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const tabName = btn.getAttribute("data-tab");
            const targetId = "tab-" + tabName;

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
