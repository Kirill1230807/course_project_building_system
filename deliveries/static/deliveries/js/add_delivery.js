 // Автоматичне приховування алертів
        setTimeout(() => {
            const alertContainer = document.getElementById("alert-container");
            if (alertContainer) alertContainer.style.display = "none";
        }, 4000);

        // Додавання нового рядка матеріалу
        function addMaterialRow() {
            const container = document.getElementById('materials-list');
            const first = container.querySelector('.material-row');
            const clone = first.cloneNode(true);

            // очищаємо поля нового рядка
            const select = clone.querySelector("select[name='material_id']");
            const qtyInput = clone.querySelector("input[name='quantity']");

            if (select) select.selectedIndex = 0;
            if (qtyInput) qtyInput.value = "";

            container.appendChild(clone);
        }

        // Видалення рядка матеріалу
        function removeMaterialRow(button) {
            const container = document.getElementById('materials-list');
            const rows = container.querySelectorAll('.material-row');

            // Якщо лише один рядок — очищаємо його
            if (rows.length === 1) {
                const select = rows[0].querySelector("select[name='material_id']");
                const qtyInput = rows[0].querySelector("input[name='quantity']");
                if (select) select.selectedIndex = 0;
                if (qtyInput) qtyInput.value = "";
                return;
            }

            // Якщо рядків більше — видаляємо той, який натиснув користувач
            const row = button.closest('.material-row');
            if (row) {
                container.removeChild(row);
            }
        }

        // Завантаження дільниць після вибору об’єкта
        document.addEventListener("DOMContentLoaded", function () {
            const siteSelect = document.querySelector("select[name='site_id']");
            const sectionSelect = document.querySelector("select[name='section_id']");

            siteSelect.addEventListener("change", function () {
                const siteId = this.value;
                sectionSelect.innerHTML = "<option>Завантаження...</option>";
                if (!siteId) return;

                fetch(`/deliveries/get-sections/${siteId}/`)
                    .then(response => response.json())
                    .then(data => {
                        sectionSelect.innerHTML = "";
                        if (data.sections.length === 0) {
                            sectionSelect.innerHTML = "<option value=''>Немає дільниць</option>";
                        } else {
                            data.sections.forEach(sec => {
                                const option = document.createElement("option");
                                option.value = sec[0];
                                option.textContent = sec[1];
                                sectionSelect.appendChild(option);
                            });
                        }
                    })
                    .catch(error => {
                        console.error("Помилка завантаження дільниць:", error);
                        sectionSelect.innerHTML = "<option value=''>Помилка</option>";
                    });
            });
        });