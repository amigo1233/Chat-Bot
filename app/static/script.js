const chatEl   = document.getElementById("chat");
const formEl   = document.getElementById("chat-form");
const inputEl  = document.getElementById("msg");
const clearBtn = document.getElementById("clear");

// ключ localStorage з урахуванням користувача
function getLSKey() {
  const appRoot = document.getElementById("app");
  const uid = appRoot?.dataset?.userId;
  return uid ? `chatHistory:${uid}` : "chatHistory"; // запасний варіант
}

// Збереження / завантаження
function saveChat() {
  localStorage.setItem(getLSKey(), chatEl.innerHTML);
}

function loadChat() {
  const saved = localStorage.getItem(getLSKey());
  if (saved) {
    chatEl.innerHTML = saved;
    chatEl.scrollTop = chatEl.scrollHeight;
  }
}

document.addEventListener("DOMContentLoaded", loadChat);

// ===== Утиліти =====
function makeBubble(role, text) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;

  const inner = document.createElement("div");
  inner.style.width = "100%";

  const tag = document.createElement("div");
  tag.className = "tag";
  tag.textContent = role === "user" ? "Ти" : "Бот";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text; // безпечно (без HTML)

  inner.appendChild(tag);
  inner.appendChild(bubble);
  wrap.appendChild(inner);
  return { wrap, bubble };
}

function append(role, text) {
  const { wrap } = makeBubble(role, text);
  chatEl.appendChild(wrap);
  chatEl.scrollTop = chatEl.scrollHeight;
  saveChat();
}

function appendAndGetBubble(role, text) {
  const { wrap, bubble } = makeBubble(role, text);
  chatEl.appendChild(wrap);
  chatEl.scrollTop = chatEl.scrollHeight;
  saveChat();
  return bubble;
}

// ===== Відправка повідомлення =====
formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = (inputEl.value || "").trim();
  if (!text) return;

  // додали твоє повідомлення
  append("user", text);
  inputEl.value = "";
  inputEl.focus();

  // заблокуємо кнопку на час запиту
  const btn = formEl.querySelector("button");
  if (btn) btn.disabled = true;

  // створимо порожню «бульбашку» бота і будемо оновлювати її
  const botBubble = appendAndGetBubble("bot", "…");

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ message: text })
    });

    if (!res.ok) throw new Error("Bad response");

    const data = await res.json();
    botBubble.textContent = data.reply ?? "(порожня відповідь)";
  } catch (err) {
    console.error(err);
    botBubble.textContent = "Сталася помилка запиту.";
  } finally {
    saveChat();
    if (btn) btn.disabled = false;
  }
});

// ===== Очистити чат =====
if (clearBtn) {
  clearBtn.addEventListener("click", async () => {
    const ok = confirm("Очистити весь чат?");
    if (!ok) return;

    try {
      const res = await fetch("/api/reset", { method: "POST" });
      const data = await res.json();

      chatEl.innerHTML = "";
      localStorage.removeItem("chatHistory");

      if (data && data.ok) {
        append("bot", "✅ Історію чату очищено.");
      } else {
        append("bot", "Не вдалося очистити чат 😕");
      }
    } catch (err) {
      console.error("Помилка запиту очищення:", err);
      chatEl.innerHTML = "";
      localStorage.removeItem("chatHistory");
      append("bot", "Помилка при очищенні чату.");
    }
  });
}

// ===== Логаут (якщо є кнопка) =====
document.addEventListener("DOMContentLoaded", () => {
  loadChat();

  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      window.location.href = "/logout";
    });
  }
});



