document.addEventListener('DOMContentLoaded', () => {

    const selectAllElements = document.getElementsByClassName('mapd-select-all-checkbox');

    for (const selectAll of selectAllElements) {
        const childSelector = selectAll.getAttribute('mapd-select-all-checkbox');
        const childCheckboxes = document.querySelectorAll(`input[name^="${childSelector}"]`);

        // When "select all" is toggled
        selectAll.addEventListener('change', (event) => {
            const checked = event.target.checked;
            for (const cb of childCheckboxes) {
                cb.checked = checked;
            }
        });

        // When any child checkbox is toggled
        for (const cb of childCheckboxes) {
            cb.addEventListener('change', () => {
                selectAll.checked = Array.from(childCheckboxes).every(cb => cb.checked);
            });
        }
    }

});