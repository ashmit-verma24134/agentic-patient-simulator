/* ================== GLOBAL STATE ================== */
console.log("🔥 FINAL SCRIPT VERSION LOADED 🔥");

let sessions = {};
let activeSessionId = null;
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
    phase: "question", // question | diagnosis | treatment | complete
  };

  setActiveSession(sessionId);
  renderSessionList();
};

/* ================== SWITCH SESSION ================== */

function setActiveSession(sessionId) {
  activeSessionId = sessionId;
  const session = sessions[sessionId];

  sessionInfo.innerText = `${session.label} • ${sessionId.slice(0, 8)}`;
  statusText.innerText = session.status;

  // 🟢 GREEN for diagnosis/treatment/complete
  if (session.phase === "question") {
    statusText.style.color = "#b91c1c"; // red
  } else {
    statusText.style.color = "#166534"; // green
  }

  // 🔒 Input control
  const allowInput = session.phase !== "complete";
  userInput.disabled = !allowInput;
  sendBtn.disabled = !allowInput;

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

/* ================== SEND MESSAGE ================== */

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
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

  /* 🚨 ERROR */
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

  /* 🟢 Diagnosis unlocked */
  if (data.next_action === "allow_diagnosis") {
    session.phase = "diagnosis";
    session.status = "Diagnosis can now be attempted";
  }

  /* ✅ Diagnosis Evaluation */
  if (data.evaluation) {
    session.chat.push({
      sender: "System",
      text: `Verdict: ${data.evaluation.verdict.toUpperCase()} — ${data.evaluation.reason}`,
      cls: "system",
    });

    if (data.evaluation.verdict === "correct") {
      session.phase = "treatment";
      session.status = "💊 Diagnosis completed — prescribe treatment";

      userInput.placeholder =
        "Prescribe treatment (e.g. treatment: rest in dark room)";
    }
  }

  /* 💊 Treatment accepted */
  if (data.treatment_verdict === "accepted") {
    session.chat.push({
      sender: "System",
      text: "Treatment accepted. Session completed.",
      cls: "system",
    });

    session.phase = "complete";
    session.status = "✅ Treatment completed";
  }

  setActiveSession(activeSessionId); // 🔥 FORCE UI SYNC
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
