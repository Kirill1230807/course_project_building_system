document.addEventListener("DOMContentLoaded", () => {

    const openBtn = document.getElementById("openAddMember");
    const modal = document.getElementById("memberModal");
    const closeBtn = document.getElementById("closeMemberModal");

    openBtn.addEventListener("click", () => {
        modal.style.display = "flex";
    });

    closeBtn.addEventListener("click", () => {
        modal.style.display = "none";
    });

    window.addEventListener("click", e => {
        if (e.target === modal) modal.style.display = "none";
    });
});
