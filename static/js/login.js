document.addEventListener("DOMContentLoaded", function () {
    const toastQueue = [];
    let isDisplaying = false;
    const pollInterval = 300;

    const toast = document.getElementById("nfc-toast");

    function showToast(message, isSuccess) {
        toast.innerText = message;
        toast.className = "toast show " + (isSuccess ? "success" : "error");

        setTimeout(() => {
            toast.classList.remove("show");
            setTimeout(() => {
                toast.className = "toast hidden";
                isDisplaying = false;
                displayNextToast();
            }, 500);
        }, 2000);
    }

    function displayNextToast() {
        if (isDisplaying || toastQueue.length === 0) return;
        const { message, success } = toastQueue.shift();
        isDisplaying = true;
        showToast(message, success);
    }

    function pollLoginMessages() {
        const secret = '';
        const whoami = '';

        // Fetch the 'whoami' value from the server
        fetch("http://localhost:5000/whoami", {
            method: "GET",
        })
        .then(res => res.json())
        .then(data => {
            whoami = data.whoami;
        });

        // Fetch the secret from the local mini flask server
        fetch("http://localhost:5000/secret", {
            method: "GET",
        })
        .then(res => res.json())
        .then(data => {
            secret = data.secret;
        });



        fetch("/nfc/wait-for-login-uid", {
            method: "POST",
            headers: {
                'Authorization': `Bearer ${secret}`,
                'whoami': whoami,
            }
        })
        .then(res => res.json())
        .then(data => {
            console.log("🔥 Poll result:", data);
            if (data.success === true && Array.isArray(data.data)) {
                const ids = [];
                data.data.forEach(entry => {
                    toastQueue.push({
                        message: entry.message,
                        success: entry.success
                    });
                    ids.push(entry.id);
                });

                // Immediately mark messages as processed
                if (ids.length > 0) {
                    acknowledgeMessages(ids);
                }

                displayNextToast();
            }
        })
        .catch(err => {
            console.error("Polling error:", err);
        })
        .finally(() => {
            setTimeout(pollLoginMessages, pollInterval);
        });
    }

    function acknowledgeMessages(ids) {
        fetch("/nfc/confirm-processed", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ids })
        }).catch(err => {
            console.error("❌ Failed to acknowledge:", err);
        });
    }

    pollLoginMessages();
});

// © 2025 Isak Landin and Compliq IT AB. All rights reserved.
// Proprietary software. Unauthorized use is prohibited.
