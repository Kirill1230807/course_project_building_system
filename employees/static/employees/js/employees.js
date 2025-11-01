document.addEventListener("DOMContentLoaded", function () {
  const categorySelect = document.getElementById("categorySelect");
  const positionSelect = document.getElementById("positionSelect");

  const allOptions = Array.from(positionSelect.options);

  categorySelect.addEventListener("change", function () {
    const selectedCat = categorySelect.value;

    // Очистити всі поточні опції
    positionSelect.innerHTML = '<option value="">— Оберіть посаду —</option>';

    // Додати тільки ті, які мають цю категорію
    allOptions.forEach(opt => {
      if (opt.dataset.category === selectedCat) {
        positionSelect.appendChild(opt);
      }
    });
  });
});
