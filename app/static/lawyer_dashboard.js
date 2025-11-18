/* ============================================================
   DOM ELEMENTS
============================================================ */
const viewDocsBtn = document.getElementById("viewDocsBtn");
const chatBtn = document.getElementById("chatBtn");

const documentsSection = document.getElementById("documentsSection");
const chatSection = document.getElementById("chatSection");
const profileSection = document.getElementById("profileSection");

const documentsList = document.getElementById("documentsList");
const chatWindow = document.getElementById("chatWindow");

const profileBtn = document.getElementById("profileBtn");
const profileView = document.getElementById("profileView");
const profileFrame = document.getElementById("profileFrame");
const profileStatus = document.getElementById("profileStatus");
const profileFile = document.getElementById("profileFile");
const uploadProfileBtn = document.getElementById("uploadProfileBtn");

const chatInput = document.getElementById("chatMessage");
const sendBtn = document.getElementById("sendBtn");

/* ============================================================
   UTILITY FUNCTIONS
============================================================ */

// Ẩn tất cả sections
function hideAllSections() {
  documentsSection.classList.add("hidden");
  chatSection.classList.add("hidden");
  profileSection.classList.add("hidden");
}

// Tạo message cho chatbot
function appendMessage(sender, text) {
  const div = document.createElement("div");
  div.className = `message ${sender}`;
  div.textContent = text;

  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

/* ============================================================
   📂 XEM TÀI LIỆU
============================================================ */
viewDocsBtn.addEventListener("click", async () => {
  hideAllSections();
  documentsSection.classList.remove("hidden");

  try {
    const response = await fetch("/lawyer/documents");
    if (!response.ok) throw new Error("Không thể tải danh sách tài liệu");
    
    const data = await response.json();
    documentsList.innerHTML = "";

    if (data.documents?.length > 0) {
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
    console.error("❌ Lỗi tải tài liệu:", error);
    documentsList.innerHTML = "<li>Lỗi khi tải danh sách tài liệu.</li>";
  }
});

/* ============================================================
   💬 CHATBOT REDIRECT
============================================================ */
chatBtn.addEventListener("click", () => {
  try {
    window.location.href = "/lawyer/chatbot";
  } catch (error) {
    console.error("❌ Lỗi chuyển chatbot:", error);
    alert("Không thể mở chatbot. Vui lòng thử lại sau.");
  }
});

/* ============================================================
   📑 HỒ SƠ CÁ NHÂN
============================================================ */
profileBtn.addEventListener("click", async () => {
  hideAllSections();
  profileSection.classList.remove("hidden");

  try {
    const res = await fetch("/lawyer/profile");
    const data = await res.json();

    if (data.exists) {
      profileView.classList.remove("hidden");
      profileFrame.src = `/profiles/${data.filename}`;
      profileStatus.textContent = "Đã tìm thấy hồ sơ. Bạn có thể thay thế bằng cách upload hồ sơ mới.";
    } else {
      profileView.classList.add("hidden");
      profileStatus.textContent = "Chưa có hồ sơ. Vui lòng tải lên.";
    }

  } catch (error) {
    console.error("❌ Lỗi kiểm tra hồ sơ:", error);
    profileStatus.textContent = "Không thể kiểm tra hồ sơ.";
  }
});

/* ============================================================
   📤 UPLOAD HỒ SƠ
============================================================ */
uploadProfileBtn.addEventListener("click", async () => {
  const file = profileFile.files[0];
  if (!file) {
    alert("Bạn chưa chọn file PDF!");
    return;
  }
  if (file.type !== "application/pdf") {
    alert("Vui lòng chỉ chọn file PDF!");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/lawyer/upload_profile", {
      method: "POST",
      body: formData
    });

    const result = await res.json();

    if (!res.ok) {
      alert("Lỗi: " + (result.detail || "Không thể upload."));
      return;
    }

    alert("Tải hồ sơ thành công!");

    // Reset file input
    profileFile.value = "";

    // Cập nhật hiển thị hồ sơ
    profileFrame.src = `/profiles/${result.filename}`;
    profileView.classList.remove("hidden");
    profileStatus.textContent = "Hồ sơ đã được cập nhật.";

  } catch (error) {
    console.error("❌ Upload error:", error);
    alert("Không thể upload hồ sơ.");
  }
});
