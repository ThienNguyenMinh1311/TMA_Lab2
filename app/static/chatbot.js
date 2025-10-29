const chatWindow = document.getElementById("chatWindow");
const sendBtn = document.getElementById("sendBtn");
const chatInput = document.getElementById("chatMessage");
const newThreadBtn = document.getElementById("newThreadBtn");
const uploadFile = document.getElementById("uploadFile");

// ======================= 💬 HIỂN THỊ LỊCH SỬ CHAT =======================
async function loadChatHistory() {
  try {
    const res = await fetch("/lawyer/chatbot/history");
    const data = await res.json();
    chatWindow.innerHTML = "";

    if (data.history && Array.isArray(data.history)) {
      data.history.forEach((msg) => {
        appendMessage(msg.role === "user" ? "user" : "bot", msg.content);
      });
    }
  } catch (error) {
    console.error("❌ Lỗi tải lịch sử:", error);
  }
}

loadChatHistory();

// ======================= 🧵 TẠO THREAD MỚI =======================
newThreadBtn.addEventListener("click", async () => {
  try {
    const res = await fetch("/lawyer/chatbot/new-thread", { method: "POST" });
    const data = await res.json();
    alert(data.message || "Đã tạo thread mới");
    chatWindow.innerHTML = "";
  } catch (err) {
    alert("Lỗi khi tạo thread mới");
  }
});

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
    alert("Lỗi khi tải tài liệu");
  }
});

// ======================= 💬 GỬI TIN NHẮN =======================
sendBtn.addEventListener("click", async () => {
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
    appendMessage("bot", data.reply || "Không có phản hồi.");
  } catch (error) {
    appendMessage("bot", "❌ Lỗi khi gửi tin nhắn.");
  }
});

// ======================= ⚙️ APPEND MESSAGE =======================
function appendMessage(sender, text) {
  const div = document.createElement("div");
  div.className = `message ${sender}`;
  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}
