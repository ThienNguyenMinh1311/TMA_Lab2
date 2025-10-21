document.addEventListener("DOMContentLoaded", () => {
  const userTableBody = document.getElementById("userTableBody");
  const editModal = document.getElementById("editUserModal");
  const closeEditModal = document.getElementById("closeEditModal");
  const accessTextarea = document.getElementById("editAccess");

  // Ẩn modal ngay khi load
  editModal.classList.add("hidden");

  closeEditModal.onclick = () => editModal.classList.add("hidden");

  // =======================
  // Load danh sách users
  // =======================
  async function loadUsers() {
    const res = await fetch("/admin/users");
    const data = await res.json();
    const users = data.users || [];
    userTableBody.innerHTML = "";

    users.forEach(user => {
      const hideDelete = user.username === "admin" ? "style='display:none;'" : "";
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${user.username}</td>
        <td>${user.role}</td>
        <td>
          <button class="btn blue" onclick="openEditUserModal('${user.username}')">✏️ Sửa</button>
          <button class="btn red" ${hideDelete} onclick="deleteUser('${user.username}')">🗑️ Xóa</button>
        </td>
      `;
      userTableBody.appendChild(row);
    });
  }

  // =======================
  // Thêm user mới
  // =======================
  document.getElementById("addUserBtn").onclick = async () => {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const role = document.getElementById("role").value;

    if (!username || !password) return alert("Nhập đầy đủ thông tin!");

    const res = await fetch("/admin/users", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({username, password, role})
    });

    if (res.ok) {
      alert("Thêm thành công!");
      document.getElementById("username").value = "";
      document.getElementById("password").value = "";
      loadUsers();
    } else {
      const data = await res.json();
      alert(data.detail || "Lỗi khi thêm!");
    }
  };

  // =======================
  // Xóa user
  // =======================
  window.deleteUser = async (username) => {
    if (!confirm(`Xóa ${username}?`)) return;

    const res = await fetch(`/admin/users/${username}`, {method: "DELETE"});
    if (res.ok) {
      alert("Đã xóa!");
      loadUsers();
    } else {
      const data = await res.json();
      alert(data.detail || "Lỗi khi xóa!");
    }
  };

  // =======================
  // Mở modal sửa user
  // =======================
  window.openEditUserModal = async (username) => {
    editModal.classList.remove("hidden");

    // Lấy thông tin user
    const res = await fetch("/admin/users");
    const data = await res.json();
    const user = data.users.find(u => u.username === username);

    document.getElementById("editUsername").value = user.username;
    document.getElementById("editRole").value = user.role;
    document.getElementById("editPassword").value = "";
    accessTextarea.value = user.access?.join(", ") || "";

    // Xóa sự kiện cũ trước khi gán mới
    const saveBtn = document.getElementById("saveEditBtn");
    saveBtn.replaceWith(saveBtn.cloneNode(true));
    const newSaveBtn = document.getElementById("saveEditBtn");

    newSaveBtn.onclick = async () => {
      const role = document.getElementById("editRole").value;
      const password = document.getElementById("editPassword").value;
      const access_input = accessTextarea.value;

      // Tách tên documents theo dấu phẩy hoặc xuống dòng
      const documents = access_input
        ? access_input.split(/[\n,]+/).map(s => s.trim()).filter(Boolean)
        : [];

      const res = await fetch(`/admin/users/${username}`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({role, password, documents})
      });

      if (res.ok) {
        alert("Cập nhật thành công!");
        editModal.classList.add("hidden");
        loadUsers();
      } else {
        const data = await res.json();
        alert(data.detail || "Lỗi khi cập nhật!");
      }
    };
  };

  // =======================
  // Khởi tạo
  // =======================
  loadUsers();
});
