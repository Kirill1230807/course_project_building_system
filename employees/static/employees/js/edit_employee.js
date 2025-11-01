document.addEventListener("DOMContentLoaded", function () {
  const categorySelect = document.getElementById("categorySelect");
  const positionSelect = document.getElementById("positionSelect");
  const allOptions = Array.from(positionSelect.options);
  const selectedCategory = categorySelect.value;

  // При завантаженні одразу відфільтрувати посади під поточну категорію
  filterPositions(selectedCategory);

  // Якщо користувач змінює категорію — оновити список посад
  categorySelect.addEventListener("change", function () {
    filterPositions(this.value);
  });

  function filterPositions(category) {
    const currentValue = positionSelect.value;
    positionSelect.innerHTML = "";
    allOptions.forEach(opt => {
      if (opt.dataset.category === category) {
        positionSelect.appendChild(opt);
      }
    });
    // Якщо попереднє значення все ще підходить — залишаємо його
    if ([...positionSelect.options].some(o => o.value === currentValue)) {
      positionSelect.value = currentValue;
    }
  }
});
