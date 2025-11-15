window.showResult = function(id) {
    const text = document.getElementById("result-" + id).textContent;
    document.getElementById("modal-data").textContent = text;
    document.getElementById("modal").style.display = "block";
};

window.closeModal = function() {
    document.getElementById("modal").style.display = "none";
};
