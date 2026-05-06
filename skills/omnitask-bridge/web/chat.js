/* omnitask-bridge · 常驻聊天窗口
   职责：WebSocket 连接 chat 后端 → 收发消息 → 渲染流式回复
*/

(function () {
  const fab = document.getElementById("chatFab");
  const panel = document.getElementById("chatPanel");
  const closeBtn = document.getElementById("chatCloseBtn");
  const clearBtn = document.getElementById("chatClearBtn");
  const stream = document.getElementById("chatStream");
  const form = document.getElementById("chatForm");
  const input = document.getElementById("chatInput");
  const sendBtn = document.getElementById("chatSendBtn");
  const dot = document.getElementById("chatHeaderDot");
  const sub = document.getElementById("chatHeaderSub");
  const badge = document.getElementById("chatFabBadge");

  let ws = null;
  let connected = false;
  let pendingBubble = null;
  let unread = 0;

  // ---------- 连接管理 ----------
  function connect() {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const url = `${proto}://${location.host}/ws/chat`;
    ws = new WebSocket(url);
    setState("connecting");

    ws.onopen = () => setState("online");
    ws.onclose = () => {
      setState("offline");
      setTimeout(connect, 3000);
    };
    ws.onerror = () => setState("error");
    ws.onmessage = (evt) => {
      try {
        handleMessage(JSON.parse(evt.data));
      } catch (e) {
        appendBubble("system", `（无法解析: ${evt.data.slice(0, 60)}…）`);
      }
    };
  }

  function setState(s) {
    connected = s === "online";
    dot.dataset.state = s;
    sub.textContent = {
      connecting: "连接中…",
      online: "在线",
      offline: "已断开 · 重连中…",
      error: "出错 · 重连中…",
    }[s] || s;
  }

  // ---------- 渲染 ----------
  function appendBubble(role, text, opts = {}) {
    const wrap = document.createElement("div");
    wrap.className = `chat-bubble chat-bubble-${role}`;
    if (opts.skill) wrap.dataset.skill = opts.skill;

    if (role === "skill_event") {
      const el = document.createElement("div");
      el.className = "chat-skill-event";
      el.textContent = text;
      wrap.appendChild(el);
    } else {
      const body = document.createElement("div");
      body.className = "chat-bubble-body";
      body.textContent = text;
      wrap.appendChild(body);
      if (opts.meta) {
        const meta = document.createElement("div");
        meta.className = "chat-bubble-meta";
        meta.textContent = opts.meta;
        wrap.appendChild(meta);
      }
    }
    stream.appendChild(wrap);
    stream.scrollTop = stream.scrollHeight;
    if (panel.hidden) {
      unread += 1;
      badge.textContent = unread > 9 ? "9+" : String(unread);
      badge.hidden = false;
    }
    return wrap;
  }

  function appendOrStreamAssistant(chunk, done) {
    if (!pendingBubble) {
      pendingBubble = appendBubble("assistant", "");
      pendingBubble.dataset.streaming = "1";
    }
    const body = pendingBubble.querySelector(".chat-bubble-body");
    if (chunk) body.textContent += chunk;
    if (done) {
      delete pendingBubble.dataset.streaming;
      pendingBubble = null;
    }
    stream.scrollTop = stream.scrollHeight;
  }

  // ---------- 消息处理 ----------
  function handleMessage(msg) {
    // 协议：
    //   {type: "ack"}                              收到了，正在路由
    //   {type: "intent", intent_class, skill, args} AI 解析结果
    //   {type: "skill_start", skill, label}        skill 开始执行
    //   {type: "skill_log", text}                  skill 中间日志
    //   {type: "skill_done", ok, summary}          skill 执行完
    //   {type: "assistant_chunk", text}            AI 回复流式片段
    //   {type: "assistant_done", text, meta}       AI 回复完成
    //   {type: "error", text}                      错误
    switch (msg.type) {
      case "ack":
        // 静默
        break;
      case "intent":
        if (msg.intent_class === "casual" || !msg.skill) break;
        appendBubble("skill_event", `🧠 已识别 → ${msg.skill}`);
        break;
      case "skill_start":
        appendBubble("skill_event", `⚙ 开始执行 ${msg.label || msg.skill}…`);
        break;
      case "skill_log":
        appendBubble("skill_event", msg.text);
        break;
      case "skill_done":
        appendBubble("skill_event", msg.ok ? `✓ ${msg.summary || "完成"}` : `✗ ${msg.summary || "失败"}`);
        break;
      case "assistant_chunk":
        appendOrStreamAssistant(msg.text, false);
        break;
      case "assistant_done":
        if (msg.text) appendOrStreamAssistant(msg.text, true);
        else appendOrStreamAssistant("", true);
        break;
      case "error":
        appendBubble("error", `⚠ ${msg.text}`);
        break;
      default:
        appendBubble("system", `（未知类型: ${msg.type}）`);
    }
  }

  // ---------- 发送 ----------
  function send(text) {
    text = text.trim();
    if (!text) return;
    appendBubble("user", text);
    if (!connected) {
      appendBubble("error", "未连接，正在重试…");
      return;
    }
    pendingBubble = null;
    ws.send(JSON.stringify({ type: "user_message", text }));
  }

  // ---------- 交互 ----------
  fab.addEventListener("click", () => {
    panel.hidden = false;
    fab.style.display = "none";
    unread = 0;
    badge.hidden = true;
    input.focus();
  });
  closeBtn.addEventListener("click", () => {
    panel.hidden = true;
    fab.style.display = "flex";
  });
  clearBtn.addEventListener("click", () => {
    stream.innerHTML = "";
  });
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = input.value;
    if (text.trim()) {
      send(text);
      input.value = "";
    }
  });
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });
  document.querySelectorAll(".chat-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      panel.hidden = false;
      fab.style.display = "none";
      send(chip.dataset.quick);
    });
  });

  // ---------- 启动 ----------
  appendBubble("assistant", "你好，跟我说话就行 — 查数据 / 下任务 / 通知合作方都可以。");
  connect();
})();
