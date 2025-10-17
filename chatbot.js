const bootstrapIconsCSS = document.createElement("link");
bootstrapIconsCSS.rel = "stylesheet";
bootstrapIconsCSS.href = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css";
document.head.appendChild(bootstrapIconsCSS);

const chatbotStyle = document.createElement("style");
chatbotStyle.innerHTML = `
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
#chatbot-toggle {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: #4f46e5;
  color: white;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  font-size: 24px;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0,0,0,0.25);
  transition: background 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}
#chatbot-toggle:hover {
  background: #4338ca;
}
#chatbox {
  position: fixed;
  bottom: 100px;
  right: 20px;
  width: 340px;
  height: 460px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
  display: none;
  flex-direction: column;
  font-family: 'Inter', sans-serif;
  transition: transform 0.3s ease, opacity 0.3s ease;
  transform: scale(0.95);
  opacity: 0;
  z-index: 9999;
}
#chatbox.show {
  display: flex;
  transform: scale(1);
  opacity: 1;
}
#chatbox-header {
  background: #4f46e5;
  color: white;
  padding: 12px 16px;
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
}
#chatbox-header button {
  background: transparent;
  color: white;
  border: none;
  font-size: 20px;
  cursor: pointer;
}
#messages {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.5;
}
.message {
  margin: 6px 0;
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 10px;
  clear: both;
  display: inline-block;
}
.user-message {
  background: #e0e7ff;
  float: right;
  text-align: left;
}
.bot-message {
  background: #f3f4f6;
  float: left;
  text-align: left;
}
#input-box {
  display: flex;
  border-top: 1px solid #eee;
  padding: 10px;
}
#user-input {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
}
#send-btn {
  background: #4f46e5;
  color: white;
  border: none;
  padding: 0 16px;
  margin-left: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}
#send-btn i {
  font-size: 18px;
}
#send-btn:hover {
  background: #4338ca;
}`;
document.head.appendChild(chatbotStyle);

document.addEventListener("DOMContentLoaded", () => {
  const chatbotHTML = `
    <button id="chatbot-toggle"><i class="bi bi-chat-dots-fill"></i></button>
    <div id="chatbox">
      <div id="chatbox-header">
        <span>Trợ lý AI</span>
        <button id="close-chatbox"><i class="bi bi-x-lg"></i></button>
      </div>
      <div id="messages"></div>
      <div id="input-box">
        <input id="user-input" placeholder="Gõ câu hỏi..." />
        <button id="send-btn"><i class="bi bi-send-fill"></i></button>
      </div>
    </div>`;

  const wrapper = document.createElement("div");
  wrapper.innerHTML = chatbotHTML;
  document.body.appendChild(wrapper);

  const toggle = document.getElementById("chatbot-toggle");
  const close = document.getElementById("close-chatbox");
  const sendBtn = document.getElementById("send-btn");
  const userInput = document.getElementById("user-input");
  const messages = document.getElementById("messages");
  const box = document.getElementById("chatbox");

  if (!toggle || !close || !sendBtn || !userInput || !messages || !box) {
    console.error("❌ Không tìm thấy phần tử chatbot trong DOM.");
    return;
  }

  toggle.onclick = () => {
    box.classList.toggle("show");
    if (box.classList.contains("show") && !messages.dataset.greeted) {
      messages.innerHTML += `<div class="message bot-message">Xin chào! Tôi sẵn sàng giúp đỡ bạn.</div>`;
      messages.dataset.greeted = "true";
    }
  };

  close.onclick = () => box.classList.remove("show");
  sendBtn.onclick = sendMessage;
  userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    messages.innerHTML += `<div class="message user-message">${text}</div>`;
    userInput.value = "";

    const loadingId = `loading-${Date.now()}`;
    messages.innerHTML += `<div class="message bot-message" id="${loadingId}"><i class="bi bi-three-dots"></i> Đang trả lời...</div>`;
    messages.scrollTop = messages.scrollHeight;

    try {
      const res = await fetch("https://71ac-171-235-249-77.ngrok-free.app/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text })
      });
      const data = await res.json();
      const formatted = data.response.replace(/\n/g, "<br>");
      document.getElementById(loadingId).innerHTML = formatted;
    } catch {
      document.getElementById(loadingId).innerHTML = "Lỗi kết nối máy chủ.";
    }

    messages.scrollTop = messages.scrollHeight;
  }
});
