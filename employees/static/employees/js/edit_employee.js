document.addEventListener("DOMContentLoaded", function () {
  const categorySelect = document.getElementById("categorySelect");
  const positionSelect = document.getElementById("positionSelect");
  const allOptions = Array.from(positionSelect.options);

  function filterPositions(category) {
    const currentValue = positionSelect.value;
    positionSelect.innerHTML = "";
    allOptions.forEach(opt => {
      if (opt.dataset.category === category) positionSelect.appendChild(opt);
    });
    if ([...positionSelect.options].some(o => o.value === currentValue)) {
      positionSelect.value = currentValue;
    }
  }

  filterPositions(categorySelect.value);
  categorySelect.addEventListener("change", () => filterPositions(categorySelect.value));

  // ✅ ЛИШЕ ЗАПИС — БЕЗ ЧИТАННЯ тут!
  const form = document.querySelector("form");
  form.addEventListener("submit", () => {
    localStorage.setItem("employeeUpdated", "✅ Дані працівника оновлено успішно!");
  });
});
