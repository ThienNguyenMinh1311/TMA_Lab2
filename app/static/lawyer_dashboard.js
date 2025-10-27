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
  try {
    // ✅ Chuyển hướng qua backend /lawyer/chatbot
    // FastAPI sẽ kiểm tra JWT và redirect đến workspace của user
    window.location.href = "/lawyer/chatbot";
  } catch (error) {
    console.error("❌ Lỗi khi chuyển hướng đến chatbot:", error);
    alert("Không thể mở chatbot. Vui lòng thử lại sau.");
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
