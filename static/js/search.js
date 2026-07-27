// StockLens - Ticker search box behavior
// Calls /search?q=... on the server and renders clickable "Add" cards.
// Shows a lightweight loading/status message so the box never feels frozen.

document.addEventListener("DOMContentLoaded", function () {
    const searchBox = document.getElementById("tickerSearchBox");
    const resultsDiv = document.getElementById("searchResults");
    const statusDiv = document.getElementById("searchStatus");

    if (!searchBox) return;

    let debounceTimer = null;

    searchBox.addEventListener("input", function () {
        const query = searchBox.value.trim();

        clearTimeout(debounceTimer);

        if (!query) {
            resultsDiv.innerHTML = "";
            statusDiv.textContent = "";
            return;
        }

        statusDiv.textContent = "Searching...";

        debounceTimer = setTimeout(() => {
            fetch("/search?q=" + encodeURIComponent(query))
                .then((res) => res.json())
                .then((data) => {
                    renderResults(data.results);
                })
                .catch(() => {
                    statusDiv.textContent = "";
                    resultsDiv.innerHTML = '<p class="text-danger">Search failed. Please try again.</p>';
                });
        }, 200);
    });

    function renderResults(results) {
        resultsDiv.innerHTML = "";

        if (!results || results.length === 0) {
            statusDiv.textContent = "";
            resultsDiv.innerHTML = '<p class="text-muted">No matching stocks found.</p>';
            return;
        }

        statusDiv.textContent = results.length + " result" + (results.length === 1 ? "" : "s") + " found";

        results.slice(0, 12).forEach((stock) => {
            const col = document.createElement("div");
            col.className = "col-md-4 col-lg-3";

            col.innerHTML = `
                <div class="border rounded p-2 d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${stock.ticker}</strong>
                        <div class="small text-muted">${stock.name}</div>
                    </div>
                    <form method="POST" action="/watchlist/add">
                        <input type="hidden" name="ticker" value="${stock.ticker}">
                        <button type="submit" class="btn btn-sm btn-success">Add</button>
                    </form>
                </div>
            `;
            resultsDiv.appendChild(col);
        });
    }
});
