const viewDocsBtn = document.getElementById("viewDocsBtn");
const chatBtn = document.getElementById("chatBtn");
const documentsSection = document.getElementById("documentsSection");
const chatSection = document.getElementById("chatSection");
const documentsList = document.getElementById("documentsList");
const chatWindow = document.getElementById("chatWindow");
const sendBtn = document.getElementById("sendBtn");
const chatInput = document.getElementById("chatMessage");

// ======================= 📂 XEM TÀI LIỆU =======================
viewDocsBtn.addEventListener("click", async () => {
  // Ẩn chatbot, hiển thị danh sách tài liệu
  chatSection.classList.add("hidden");
  documentsSection.classList.remove("hidden");

  try {
    const response = await fetch("/lawyer/documents");
    if (!response.ok) throw new Error("Không thể tải danh sách tài liệu");
    const data = await response.json();

    documentsList.innerHTML = "";

    if (data.documents && data.documents.length > 0) {
      data.documents.forEach((doc) => {
        const li = document.createElement("li");
        const btn = document.createElement("button");

        btn.textContent = `📄 ${doc}`;
        btn.className = "doc-btn";
        // ⚙️ Đường dẫn tuyệt đối tránh lỗi /lawyer/dataset/
        btn.onclick = () => window.open(`${window.location.origin}/dataset/${doc}`, "_blank");
        li.appendChild(btn);
        documentsList.appendChild(li);
      });
    } else {
      documentsList.innerHTML = "<li>Không có tài liệu nào được phép truy cập.</li>";
    }
  } catch (error) {
    console.error("❌ Lỗi khi tải tài liệu:", error);
    documentsList.innerHTML = "<li>Lỗi khi tải danh sách tài liệu.</li>";
  }
});

// ======================= 💬 CHATBOT =======================
chatBtn.addEventListener("click", () => {
  documentsSection.classList.add("hidden");
  chatSection.classList.remove("hidden");
});

sendBtn.addEventListener("click", async () => {
  const msg = chatInput.value.trim();
  if (!msg) return;

  appendMessage("user", msg);
  chatInput.value = "";

  try {
    const res = await fetch("/api/chatbot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    });

    if (!res.ok) throw new Error("Chatbot không phản hồi.");
    const data = await res.json();

    appendMessage("bot", data.reply || "Bot không có phản hồi.");
  } catch (error) {
    appendMessage("bot", "⚠️ Lỗi khi gửi tin nhắn tới chatbot.");
    console.error(error);
  }
});

// ======================= 💬 APPEND MESSAGE =======================
function appendMessage(sender, text) {
  const div = document.createElement("div");
  div.className = `message ${sender}`;
  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}
