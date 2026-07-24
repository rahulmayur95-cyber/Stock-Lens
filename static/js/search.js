// StockLens - Ticker search box behavior
// Calls /search?q=... on the server (which filters the curated tickers.py list)
// and renders clickable "Add" cards into #searchResults.

document.addEventListener("DOMContentLoaded", function () {
    const searchBox = document.getElementById("tickerSearchBox");
    const resultsDiv = document.getElementById("searchResults");

    if (!searchBox) return;

    let debounceTimer = null;

    searchBox.addEventListener("input", function () {
        const query = searchBox.value.trim();

        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            fetch("/search?q=" + encodeURIComponent(query))
                .then((res) => res.json())
                .then((data) => {
                    renderResults(data.results);
                })
                .catch(() => {
                    resultsDiv.innerHTML = '<p class="text-danger">Search failed. Please try again.</p>';
                });
        }, 200);
    });

    function renderResults(results) {
        resultsDiv.innerHTML = "";

        if (!results || results.length === 0) {
            resultsDiv.innerHTML = '<p class="text-muted">No matching stocks found.</p>';
            return;
        }

        // Limit to first 12 shown at once to keep the UI clean
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
