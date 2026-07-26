// StockLens - Client-side sortable table for Compare view.
// Clicking a header sorts the table by that column, toggling ascending/descending.

document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("compareTable");
    if (!table) return;

    const headers = table.querySelectorAll("thead th");
    let currentSort = { columnIndex: null, ascending: true };

    headers.forEach((header, columnIndex) => {
        header.addEventListener("click", () => {
            const type = header.getAttribute("data-type");
            if (!type) return; // "Alert" column has no data-type, skip sorting it

            const ascending = currentSort.columnIndex === columnIndex ? !currentSort.ascending : true;
            currentSort = { columnIndex, ascending };

            const tbody = table.querySelector("tbody");
            const rows = Array.from(tbody.querySelectorAll("tr"));

            rows.sort((rowA, rowB) => {
                const cellA = rowA.children[columnIndex].textContent.trim();
                const cellB = rowB.children[columnIndex].textContent.trim();

                let valueA, valueB;
                if (type === "number") {
                    valueA = parseFloat(cellA.replace(/[^0-9.\-]/g, ""));
                    valueB = parseFloat(cellB.replace(/[^0-9.\-]/g, ""));
                    if (isNaN(valueA)) valueA = -Infinity;
                    if (isNaN(valueB)) valueB = -Infinity;
                } else {
                    valueA = cellA.toLowerCase();
                    valueB = cellB.toLowerCase();
                }

                if (valueA < valueB) return ascending ? -1 : 1;
                if (valueA > valueB) return ascending ? 1 : -1;
                return 0;
            });

            rows.forEach((row) => tbody.appendChild(row));
        });
    });
});
