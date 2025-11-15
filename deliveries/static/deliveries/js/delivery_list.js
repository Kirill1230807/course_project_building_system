document.getElementById('siteSelect').addEventListener('change', function () {
            const siteId = this.value;
            const sectionSelect = document.getElementById('sectionSelect');
            sectionSelect.innerHTML = '<option>Завантаження...</option>';
            sectionSelect.disabled = true;

            if (siteId) {
                fetch(`/deliveries/get-sections/${siteId}/`)
                    .then(res => res.json())
                    .then(data => {
                        sectionSelect.innerHTML = '<option value="">Усі</option>';
                        data.sections.forEach(s => {
                            sectionSelect.innerHTML += `<option value="${s[0]}">${s[1]}</option>`;
                        });
                        sectionSelect.disabled = false;
                    });
            } else {
                sectionSelect.innerHTML = '<option value="">Усі</option>';
                sectionSelect.disabled = true;
            }
        });