function fetchLoggedInUsers() {
    fetch("/export/json")
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector(".user-table tbody");
            tbody.innerHTML = ""; // Clear current list

            if (data.length === 0) {
                const row = document.createElement("tr");
                row.innerHTML = `<td colspan="3">Inga användare inloggade än.</td>`;
                tbody.appendChild(row);
                return;
            }

            data.forEach(user => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${user.user_name}</td>
                    <td>${user.tag_id}</td>
                    <td data-order="${user.last_scan_iso}">${user.last_scan_time}</td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error("Fel vid hämtning av inloggade användare:", error);
        });
}

// Initial fetch + poll every 5 seconds
fetchLoggedInUsers();
setInterval(fetchLoggedInUsers, 5000);
