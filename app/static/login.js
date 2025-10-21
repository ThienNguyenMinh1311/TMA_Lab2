document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const errorMsg = document.getElementById("errorMsg");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    try {
      const response = await fetch("/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Đăng nhập thất bại");
      }

      console.log("Đăng nhập thành công:", data);
      errorMsg.textContent = "";
      errorMsg.style.color = "";

      if (data.role === "admin") {
        window.location.href = "/admin/dashboard";
      } else {
        window.location.href = "/lawyer/dashboard";
      }
    } catch (err) {
      errorMsg.textContent = err.message;
      errorMsg.style.color = "red";
    }
  });
});