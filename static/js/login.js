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
        let secret = '';
        let whoami = '';

        // Fetch whoami first
        fetch("http://localhost:5000/whoami")
            .then(res => res.json())
            .then(data => {
                whoami = data.whoami;

                // Fetch secret next
                return fetch("http://localhost:5000/secret");
            })
            .then(res => res.json())
            .then(data => {
                secret = data.secret;


                return fetch("/nfc/wait-for-login-uid", {
                    method: "POST",
                    headers: {
                        'Authorization': `Bearer ${secret}`,
                        'whoami': whoami,
                    }
                });
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
    let secret = '';

    // Fetch secret first, then continue
    fetch("http://localhost:5000/secret")
        .then(res => res.json())
        .then(data => {
            secret = data.secret;

            // Now acknowledge messages
            return fetch("/nfc/confirm-processed", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${secret}`
                },
                body: JSON.stringify({ ids })
            });
        })
        .catch(err => {
            console.error("❌ Failed to acknowledge:", err);
        });
    }

    pollLoginMessages();
});

// © 2025 Isak Landin and Compliq IT AB. All rights reserved.
// Proprietary software. Unauthorized use is prohibited.
