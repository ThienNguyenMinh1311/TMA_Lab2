document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const errorMsg = document.getElementById("errorMsg");

  try {
    const res = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    if (!res.ok) {
      errorMsg.textContent = data.detail || "Sai tài khoản hoặc mật khẩu";
      return;
    }

    localStorage.setItem("username", data.username);
    if (data.username.startsWith("admin")) {
      window.location.href = "/admin/dashboard";
    } else {
      window.location.href = "/lawyer/dashboard";
    }
  } catch (error) {
    errorMsg.textContent = "Lỗi kết nối máy chủ.";
  }
});