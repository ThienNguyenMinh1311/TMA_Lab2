const chatWindow = document.getElementById("chatWindow");
const sendBtn = document.getElementById("sendBtn");
const chatInput = document.getElementById("chatMessage");
const uploadFile = document.getElementById("uploadFile");


// ======================= 💬 LOAD LỊCH SỬ CHAT =======================
async function loadChatHistory() {
  try {
    const res = await fetch("/lawyer/chatbot/history");
    const data = await res.json();

    chatWindow.innerHTML = "";

    if (!data.history || !Array.isArray(data.history)) return;

    data.history.forEach((msg) => {
      appendMessage(msg.role, msg.content);
    });
  } catch (error) {
    console.error("❌ Lỗi tải lịch sử:", error);
  }
}

loadChatHistory();


// ======================= 📤 UPLOAD FILE =======================
uploadFile.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/lawyer/chatbot/upload-doc", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    alert(data.message || "Tải lên thành công");
  } catch (error) {
    alert("❌ Lỗi khi tải tài liệu");
  }
});


// ======================= 💬 GỬI TIN NHẮN =======================
sendBtn.addEventListener("click", sendMessage);
chatInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  appendMessage("user", text);
  chatInput.value = "";

  try {
    const res = await fetch("/lawyer/chatbot/send-message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    const data = await res.json();
    appendMessage("assistant", data.reply || "Không có phản hồi.");
  } catch (error) {
    appendMessage("assistant", "❌ Lỗi khi gửi tin nhắn.");
  }
}


// ======================= ⚙️ HIỂN THỊ TIN NHẮN =======================
function appendMessage(role, text) {
  const div = document.createElement("div");

  if (role === "user") {
    div.className = "message user";
  } else {
    div.className = "message bot";
  }

  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}
