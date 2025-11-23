const chatWindow = document.getElementById("chatWindow");
const sendBtn = document.getElementById("sendBtn");
const chatInput = document.getElementById("chatMessage");
const uploadFile = document.getElementById("uploadFile");


// ======================= 💬 LOAD LỊCH SỬ CHAT =======================
async function loadChatHistory() {
  try {
    const res = await fetch("/admin/chatbot/history");
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

// ======================= 📤 UPDATE ALL PROFILES =======================
const updateProfilesBtn = document.getElementById("updateProfilesBtn");

updateProfilesBtn.addEventListener("click", async () => {
  updateProfilesBtn.disabled = true;
  updateProfilesBtn.textContent = "⏳ Đang cập nhật...";

  try {
    const res = await fetch("/admin/chatbot/upload-all", {
      method: "POST"
    });

    const data = await res.json();
    alert(data.message || "Đã tải toàn bộ hồ sơ.");
  } catch (error) {
    console.error("❌ Lỗi khi tải hồ sơ:", error);
    alert("❌ Lỗi khi upload toàn bộ hồ sơ");
  } finally {
    updateProfilesBtn.disabled = false;
    updateProfilesBtn.textContent = "🔄 Cập nhật hồ sơ (tự động)";
  }
});

// ======================= ⚙️ CHẾ ĐỘ CHAT/QUERY =======================
let currentMode = "chat"; // mặc định chat

const modeButtons = document.querySelectorAll(".mode-btn");

modeButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    modeButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentMode = btn.dataset.mode;
    console.log("Chế độ hiện tại:", currentMode);

    // Optional: đổi placeholder input theo chế độ
    chatInput.placeholder = currentMode === "chat"
      ? "Nhập tin nhắn..."
      : "Nhập truy vấn hồ sơ của các luật sư...";
  });
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
    const res = await fetch("/admin/chatbot/send-message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        message: text,
        mode: currentMode}),
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
