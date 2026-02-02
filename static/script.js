// ================= CHATBOT MESSAGE FUNCTION =================
function sendMessage() {
    const input = document.getElementById("chatInput");
    const replyBox = document.getElementById("chatReply");

    const message = input.value.trim();
    if (message === "") return;

    replyBox.innerHTML = "Thinking...";

    fetch("/chatbot", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        replyBox.innerHTML = data.reply;
    })
    .catch(() => {
        replyBox.innerHTML = "⚠️ Server error. Try again.";
    });

    input.value = "";
}

// ================= TOGGLE CHATBOX (ROBOT BUTTON) =================
function toggleChat() {
    const chatbox = document.getElementById("chatbox");
    if (chatbox.style.display === "block") {
        chatbox.style.display = "none";
    } else {
        chatbox.style.display = "block";
    }
}

// ================= SCORE CIRCLE ANIMATION =================
document.addEventListener("DOMContentLoaded", function () {
    const circle = document.querySelector(".score-circle");
    if (!circle) return;

    const score = circle.getAttribute("data-score");
    circle.style.setProperty("--score", score);
});
