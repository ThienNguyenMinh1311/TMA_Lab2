const API_BASE = "http://localhost:8000/admin"; // Đổi nếu bạn deploy server khác
let users = [];
let documents = [];
let currentEditUser = null;

// =============================
// 🔹 HIỂN THỊ GIAO DIỆN
// =============================
function showSection(section) {
  document.querySelectorAll("section").forEach((s) => (s.style.display = "none"));
  document.getElementById(`${section}-section`).style.display = "block";

  if (section === "lawyer") loadUsers();
  else if (section === "document") loadDocuments();
}

// =============================
// 🔹 QUẢN LÝ LUẬT SƯ
// =============================
async function loadUsers() {
  try {
    const res = await fetch(`${API_BASE}/users`);
    const data = await res.json();
    users = data.users || [];
    renderUserTable();
  } catch (err) {
    console.error("Lỗi tải danh sách người dùng:", err);
    alert("Không thể tải danh sách người dùng!");
  }
}

function renderUserTable() {
  const tbody = document.getElementById("lawyer-table");
  tbody.innerHTML = "";

  users.forEach((user) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${user.username}</td>
      <td>${user.role}</td>
      <td>${(user.access || []).join(", ") || "—"}</td>
      <td>
        <button onclick="openEditModal('${user.username}')">Sửa</button>
        <button onclick="deleteUser('${user.username}')" ${user.role === "admin" ? "disabled" : ""}>Xóa</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function showAddForm() {
  const modal = createModal("Thêm luật sư mới", [
    { label: "Tên tài khoản", id: "newUsername", type: "text" },
    { label: "Mật khẩu", id: "newPassword", type: "password" },
    {
      label: "Vai trò",
      id: "newRole",
      type: "select",
      options: ["lawyer", "admin"],
    },
    {
      label: "Tài liệu được truy cập (phân tách bằng dấu phẩy)",
      id: "newAccess",
      type: "text",
    },
  ]);

  const submitBtn = document.createElement("button");
  submitBtn.textContent = "Thêm";
  submitBtn.onclick = addUser;
  modal.querySelector(".modal-content").appendChild(submitBtn);
  document.body.appendChild(modal);
}

async function addUser() {
  const username = document.getElementById("newUsername").value.trim();
  const password = document.getElementById("newPassword").value.trim();
  const role = document.getElementById("newRole").value;
  const accessText = document.getElementById("newAccess").value.trim();
  const access = accessText ? accessText.split(",").map((s) => s.trim()) : [];

  if (!username || !password) return alert("Vui lòng nhập đầy đủ thông tin!");

  try {
    const res = await fetch(`${API_BASE}/users`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, role, access }),
    });
    if (!res.ok) throw new Error("Thêm người dùng thất bại");
    alert("✅ Thêm luật sư thành công!");
    closeAllModals();
    await loadUsers();
  } catch (err) {
    alert("❌ Lỗi khi thêm người dùng!");
    console.error(err);
  }
}

function openEditModal(username) {
  const user = users.find((u) => u.username === username);
  if (!user) return;

  currentEditUser = user;
  const modal = createModal("Sửa thông tin người dùng", [
    { label: "Tên tài khoản", id: "editUsername", type: "text", value: user.username, disabled: true },
    { label: "Mật khẩu mới (nếu muốn thay đổi)", id: "editPassword", type: "password" },
    { label: "Vai trò", id: "editRole", type: "select", options: ["lawyer", "admin"], value: user.role },
    {
      label: "Tài liệu được truy cập (phân tách bằng dấu phẩy)",
      id: "editAccess",
      type: "text",
      value: (user.access || []).join(", "),
    },
  ]);

  const saveBtn = document.createElement("button");
  saveBtn.textContent = "Lưu thay đổi";
  saveBtn.onclick = saveEdit;
  modal.querySelector(".modal-content").appendChild(saveBtn);
  document.body.appendChild(modal);
}

async function saveEdit() {
  const username = document.getElementById("editUsername").value;
  const password = document.getElementById("editPassword").value.trim();
  const role = document.getElementById("editRole").value;
  const accessText = document.getElementById("editAccess").value.trim();
  const documents = accessText ? accessText.split(",").map((s) => s.trim()) : [];

  try {
    const res = await fetch(`${API_BASE}/users/${username}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password, role, documents }),
    });
    if (!res.ok) throw new Error("Cập nhật thất bại");
    alert("✅ Cập nhật thành công!");
    closeAllModals();
    await loadUsers();
  } catch (err) {
    alert("❌ Lỗi khi cập nhật người dùng!");
    console.error(err);
  }
}

async function deleteUser(username) {
  if (!confirm(`Bạn có chắc muốn xóa '${username}' không?`)) return;

  try {
    const res = await fetch(`${API_BASE}/users/${username}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Xóa thất bại");
    alert("✅ Xóa người dùng thành công!");
    await loadUsers();
  } catch (err) {
    alert("❌ Lỗi khi xóa người dùng!");
    console.error(err);
  }
}

// =============================
// 🔹 QUẢN LÝ TÀI LIỆU
// =============================
async function loadDocuments() {
  try {
    const res = await fetch(`${API_BASE.replace("/admin", "")}/admin/documents`);
    const data = await res.json();
    const tbody = document.getElementById("document-table");
    tbody.innerHTML = "";

    (data.documents || []).forEach(doc => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${doc}</td>
        <td>
          <button onclick="deleteDocument('${doc}')">🗑️ Xóa</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Lỗi tải tài liệu:", err);
    alert("Không thể tải danh sách tài liệu!");
  }
}

// =============================
// 🔹 UPLOAD TÀI LIỆU
// =============================
async function uploadDocuments() {
  const input = document.getElementById("documentFile");
  if (!input.files.length) {
    alert("Vui lòng chọn ít nhất một file!");
    return;
  }

  const formData = new FormData();
  for (const file of input.files) {
    formData.append("files", file);
  }

  try {
    const res = await fetch(`${API_BASE.replace("/admin", "")}/admin/documents/upload`, {
      method: "POST",
      body: formData
    });
    if (!res.ok) throw new Error("Upload thất bại");
    alert("✅ Upload thành công!");
    input.value = "";
    await loadDocuments();
  } catch (err) {
    console.error("Lỗi upload:", err);
    alert("❌ Lỗi khi tải lên tài liệu!");
  }
}

// =============================
// 🔹 XÓA TÀI LIỆU
// =============================
async function deleteDocument(filename) {
  if (!confirm(`Bạn có chắc muốn xóa '${filename}' không?`)) return;

  try {
    const res = await fetch(`${API_BASE.replace("/admin", "")}/admin/documents/${filename}`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error("Xóa thất bại");
    alert("🗑️ Đã xóa tài liệu!");
    await loadDocuments();
  } catch (err) {
    console.error("Lỗi xóa tài liệu:", err);
    alert("❌ Lỗi khi xóa tài liệu!");
  }
}


// =============================
// 🔹 MODAL DÙNG CHUNG
// =============================
function createModal(title, fields) {
  closeAllModals();
  const modal = document.createElement("div");
  modal.className = "modal";
  modal.style.display = "flex";

  const content = document.createElement("div");
  content.className = "modal-content";

  const closeBtn = document.createElement("button");
  closeBtn.className = "close";
  closeBtn.textContent = "×";
  closeBtn.onclick = () => closeAllModals();

  const heading = document.createElement("h3");
  heading.textContent = title;

  content.appendChild(closeBtn);
  content.appendChild(heading);

  fields.forEach((f) => {
    const label = document.createElement("label");
    label.textContent = f.label;

    let input;
    if (f.type === "select") {
      input = document.createElement("select");
      f.options.forEach((opt) => {
        const option = document.createElement("option");
        option.value = opt;
        option.textContent = opt;
        if (f.value === opt) option.selected = true;
        input.appendChild(option);
      });
    } else {
      input = document.createElement("input");
      input.type = f.type;
      input.value = f.value || "";
    }

    input.id = f.id;
    if (f.disabled) input.disabled = true;

    content.appendChild(label);
    content.appendChild(input);
  });

  modal.appendChild(content);
  return modal;
}

function closeAllModals() {
  document.querySelectorAll(".modal").forEach((m) => m.remove());
}

// =============================
// 🔹 KHỞI TẠO MẶC ĐỊNH
// =============================
window.onload = () => showSection("lawyer");
