document.addEventListener("DOMContentLoaded", function () {
    const toastQueue = [];
    let isDisplaying = false;

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

    function acknowledgeMessages(ids) {
        fetch("http://localhost:5000/secret")
            .then(res => res.json())
            .then(data => {
                return fetch("/nfc/backend/confirm-processed", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${data.secret}`
                    },
                    body: JSON.stringify({ ids })
                });
            })
            .catch(err => {
                console.error("❌ Failed to acknowledge:", err);
            });
    }

    // Retrieve whoami + secret, then open SSE connection
    Promise.all([
        fetch("http://localhost:5000/whoami").then(res => res.json()),
        fetch("http://localhost:5000/secret").then(res => res.json())
    ]).then(([whoamiData, secretData]) => {
        const whoami = whoamiData.whoami;
        const secret = secretData.secret;

        const source = new EventSource(`/nfc/backend/login-sse?whoami=${whoami}&secret=${secret}`);

        source.onmessage = function (event) {
            const data = JSON.parse(event.data);

            toastQueue.push({
                message: data.message,
                success: data.success
            });

            if (data.id) {
                acknowledgeMessages([data.id]);
            }

            displayNextToast();
        };

        source.onerror = function (err) {
            console.error("🔌 SSE connection lost:", err);
            // Optionally reconnect with a delay
        };
    });
});
