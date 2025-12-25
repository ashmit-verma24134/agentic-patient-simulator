/* ================== GLOBAL STATE ================== */

let sessions = {};              // all patient sessions
let activeSessionId = null;     // currently selected patient
let patientCounter = 1;

/* ================== DOM ================== */

const chatBox = document.getElementById("chatBox");
const sessionInfo = document.getElementById("sessionInfo");
const statusText = document.getElementById("status");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const createSessionBtn = document.getElementById("createSessionBtn");
const sessionList = document.getElementById("sessionList");
const chatForm = document.getElementById("chatForm");

/* ================== INITIAL STATE ================== */

userInput.disabled = true;
sendBtn.disabled = true;

/* ================== CREATE SESSION ================== */

createSessionBtn.onclick = async () => {
  const res = await fetch("http://127.0.0.1:5000/create_session", {
    method: "POST",
  });

  const data = await res.json();
  const sessionId = data.session_id;

  sessions[sessionId] = {
    label: `Patient ${patientCounter++}`,
    chat: [],
    status: "Diagnosis not allowed yet",
    locked: false,
  };

  setActiveSession(sessionId);
  renderSessionList();
};

/* ================== SWITCH SESSION ================== */

function setActiveSession(sessionId) {
  activeSessionId = sessionId;
  const session = sessions[sessionId];

  sessionInfo.innerText =
    `${session.label} • ${sessionId.slice(0, 8)}`;

  statusText.innerText = session.status;
  statusText.style.color =
    session.status.includes("not") ? "#b91c1c" : "#166534";

  userInput.disabled = session.locked;
  sendBtn.disabled = session.locked;

  renderChat();
  renderSessionList();
}

/* ================== SESSION LIST ================== */

function renderSessionList() {
  sessionList.innerHTML = "";

  Object.keys(sessions).forEach((id) => {
    const div = document.createElement("div");
    div.className =
      "session-item" + (id === activeSessionId ? " active" : "");
    div.innerText = sessions[id].label;
    div.onclick = () => setActiveSession(id);
    sessionList.appendChild(div);
  });
}

/* ================== SEND MESSAGE (FORM SUBMIT) ================== */

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault(); // 🔥 REQUIRED

  if (!activeSessionId) return;

  const message = userInput.value.trim();
  if (!message) return;

  userInput.value = "";

  const res = await fetch("http://127.0.0.1:5000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: activeSessionId,
      message,
    }),
  });

  const data = await res.json();
  const session = sessions[activeSessionId];

  /* 🚨 ERROR FIRST */
  if (data.error) {
    session.chat.push({
      sender: "System",
      text: data.error,
      cls: "system",
    });
    renderChat();
    return;
  }

  /* 👨‍⚕️ Doctor */
  session.chat.push({
    sender: "Doctor",
    text: message,
    cls: "user",
  });

  /* 🧠 Patient */
  if (data.reply) {
    session.chat.push({
      sender: "Patient",
      text: data.reply,
      cls: "patient",
    });
  }

  /* 🟢 Diagnosis allowed */
  if (data.next_action === "allow_diagnosis") {
    session.status = "Diagnosis can now be attempted";
    statusText.innerText = session.status;
    statusText.style.color = "#166534";
  }

  /* ✅ Evaluation */
  if (data.evaluation) {
    session.chat.push({
      sender: "System",
      text: `Verdict: ${data.evaluation.verdict.toUpperCase()} — ${data.evaluation.reason}`,
      cls: "system",
    });

    if (data.evaluation.verdict === "correct") {
      session.status = "✅ Diagnosis completed";
      session.locked = true;
      userInput.disabled = true;
      sendBtn.disabled = true;
      statusText.innerText = session.status;
      statusText.style.color = "#166534";
    }
  }

  renderChat();
});

/* ================== RENDER CHAT ================== */

function renderChat() {
  chatBox.innerHTML = "";

  if (!activeSessionId) return;

  sessions[activeSessionId].chat.forEach((m) => {
    const div = document.createElement("div");
    div.className = "message " + m.cls;
    div.innerText = `${m.sender}: ${m.text}`;
    chatBox.appendChild(div);
  });

  chatBox.scrollTop = chatBox.scrollHeight;
}
