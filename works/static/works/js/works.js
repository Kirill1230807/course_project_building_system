document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("modal");
    const openBtn = document.getElementById("openModalBtn");
    const closeBtn = document.getElementById("closeModalBtn");

    if (openBtn && closeBtn && modal) {
        openBtn.onclick = function () {
            modal.style.display = "block";
        };

        closeBtn.onclick = function () {
            modal.style.display = "none";
        };

        window.onclick = function (event) {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        };
    }
});
