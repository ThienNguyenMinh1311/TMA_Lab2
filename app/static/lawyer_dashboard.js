const viewDocsBtn = document.getElementById("viewDocsBtn");
const chatBtn = document.getElementById("chatBtn");
const docsSection = document.getElementById("documentsSection");
const chatSection = document.getElementById("chatSection");
const docsList = document.getElementById("documentsList");
const chatWindow = document.getElementById("chatWindow");
const sendBtn = document.getElementById("sendBtn");
const chatInput = document.getElementById("chatMessage");

// Toggle hiển thị phần xem tài liệu
viewDocsBtn.addEventListener("click", async () => {
  chatSection.classList.add("hidden");
  documentsSection.classList.remove("hidden");

  const response = await fetch("/lawyer/documents");
  const data = await response.json();

  documentsList.innerHTML = "";

  if (data.documents && data.documents.length > 0) {
    data.documents.forEach((doc) => {
      const li = document.createElement("li");
      const btn = document.createElement("button");
      btn.textContent = doc;
      btn.className = "doc-btn";
      btn.onclick = () => window.open(`./dataset/${doc}`, "_blank");
      li.appendChild(btn);
      documentsList.appendChild(li);
    });
  } else {
    documentsList.innerHTML = "<li>Không có tài liệu nào được phép truy cập.</li>";
  }
});


// Xem chi tiết tài liệu
async function viewDocument(id) {
  const res = await fetch(`/api/lawyer/documents/${id}`);
  const data = await res.json();
  alert(`📄 Tiêu đề: ${data.title}\n\n${data.content}`);
}

// Giao diện chatbot
chatBtn.addEventListener("click", () => {
  docsSection.classList.add("hidden");
  chatSection.classList.remove("hidden");
});

sendBtn.addEventListener("click", async () => {
  const msg = chatInput.value.trim();
  if (!msg) return;

  appendMessage("user", msg);
  chatInput.value = "";

  // Gửi tin nhắn tới chatbot
  const res = await fetch("/api/chatbot", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg })
  });
  const data = await res.json();
  appendMessage("bot", data.reply);
});

function appendMessage(sender, text) {
  const div = document.createElement("div");
  div.className = `message ${sender}`;
  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}
