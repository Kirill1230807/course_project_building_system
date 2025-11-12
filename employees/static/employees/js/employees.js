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

    // ===== Після сабміту форми — зберегти повідомлення в localStorage =====
    const form = modal.querySelector("form");
    form.addEventListener("submit", function () {
        localStorage.setItem("employeeAdded", "Працівника додано успішно!");
    });

    // ===== При завантаженні сторінки — показати повідомлення (додавання або редагування) =====
    const addMsg = localStorage.getItem("employeeAdded");
    const updateMsg = localStorage.getItem("employeeUpdated");

    if (addMsg) {
        showMessage(addMsg);
        localStorage.removeItem("employeeAdded");
    } else if (updateMsg) {
        showMessage(updateMsg);
        localStorage.removeItem("employeeUpdated");
    }

    // ===== Функція показу повідомлення =====
    function showMessage(text) {
        const msg = document.createElement("div");
        msg.classList.add("toast-message");
        msg.textContent = text;
        document.body.appendChild(msg);

        // Якщо повідомлення про видалення — робимо червоним
        if (text.includes("")) msg.classList.add("delete");

        // Плавна поява
        setTimeout(() => msg.classList.add("show"), 100);

        // Плавне зникнення через 5 секунд
        setTimeout(() => {
            msg.classList.remove("show");
            setTimeout(() => msg.remove(), 600);
        }, 5000);

    }

    // ===== Функція підтвердження видалення =====
    window.confirmDelete = function (fullName) {
        const confirmed = confirm(`Видалити працівника ${fullName}?`);
        if (confirmed) {
            // Зберігаємо повідомлення перед переходом
            localStorage.setItem("employeeDeleted", `Працівника ${fullName} успішно видалено!`);
            return true; // продовжує перехід за посиланням
        }
        return false;
    };

    // ===== Показ повідомлення після видалення =====
    const deletedMsg = localStorage.getItem("employeeDeleted");
    if (deletedMsg) {
        showMessage(deletedMsg);
        localStorage.removeItem("employeeDeleted");
    }

});
