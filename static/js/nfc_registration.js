function startNfcScan(inputId) {
    // Always register for tag assignment
    fetch('/nfc/backend/set-nfc-status', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer etbUcfPFEgWZ3ZEET8ySjCVvjzkBoVzMeVdtBACRj3D9DCeFEQEHZvZg84osWCjMQzmU5jmhcubLSF7Dk2cHfPdY5BFrJzSNiWKo',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ value: 'register' })
    })
    .then(() => {
        showScanStatus(inputId, "Väntar på tagg...");
        pollForScanResult(inputId);
    })
    .catch(err => {
        console.error('Failed to set scan mode:', err);
        showScanStatus(inputId, "Kunde inte starta scanning.");
    });
}

function pollForScanResult(inputId) {
    let attempts = 0;
    const maxAttempts = 30;

    const intervalId = setInterval(() => {
        fetch('/nfc/wait-for-registration-uid', {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer etbUcfPFEgWZ3ZEET8ySjCVvjzkBoVzMeVdtBACRj3D9DCeFEQEHZvZg84osWCjMQzmU5jmhcubLSF7Dk2cHfPdY5BFrJzSNiWKo'
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data && data.uid) {
                clearInterval(intervalId);
                document.getElementById(inputId).value = data.uid;
                showScanStatus(inputId, "Tagg registrerad!");
                setTimeout(() => hideScanStatus(inputId), 2000);
            } else if (++attempts >= maxAttempts) {
                clearInterval(intervalId);
                showScanStatus(inputId, "Ingen tagg skannades i tid.");
            }
        })
        .catch(err => {
            clearInterval(intervalId);
            console.error('Polling error:', err);
            showScanStatus(inputId, "Polling misslyckades.");
        });
    }, 1000);
}

function showScanStatus(inputId, message) {
    const statusElement = inputId === "new-tag-id"
        ? document.getElementById("add-scan-status")
        : document.getElementById("edit-scan-status");
    if (statusElement) {
        statusElement.innerText = message;
        statusElement.classList.remove("hidden");
    }
}

function hideScanStatus(inputId) {
    const statusElement = inputId === "new-tag-id"
        ? document.getElementById("add-scan-status")
        : document.getElementById("edit-scan-status");
    if (statusElement) {
        statusElement.classList.add("hidden");
    }
}

// © 2025 Isak Landin and Compliq IT AB. All rights reserved.
// Proprietary software. Unauthorized use is prohibited.
