let sessions = {};
let activeSessionId = null;
let patientCounter = 1;
const chatBox = document.getElementById("chatBox");
const sessionInfo = document.getElementById("sessionInfo");
const statusText = document.getElementById("status");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const createSessionBtn = document.getElementById("createSessionBtn");
const sessionList = document.getElementById("sessionList");
const chatForm = document.getElementById("chatForm");
const typingIndicator = document.getElementById("typingIndicator");
const memoryList = document.getElementById("memoryList");
const confidenceBars = document.getElementById("confidenceBars");

userInput.disabled = true;
sendBtn.disabled = true;
userInput.placeholder = "Create a patient to begin";


function showTypingIndicator(show) {
  typingIndicator.style.display = show ? "block" : "none";
}

function updateMemory(symptoms = []) {
  memoryList.innerHTML = "";
  symptoms.forEach(s => {const li = document.createElement("li");li.innerText = `✔ ${s}`;memoryList.appendChild(li);});
}

function updateConfidenceBars(confidence = {}) {
  confidenceBars.innerHTML = "";
  Object.keys(confidence).forEach(disease => {
    const percent = confidence[disease];
    const wrapper = document.createElement("div");
    wrapper.className = "bar-container";
    wrapper.innerHTML = `
      <div class="bar-label">${disease} — ${percent}%</div>
      <div class="bar-bg">
        <div class="bar-fill" style="width:${percent}%"></div>
      </div>
    `;
    confidenceBars.appendChild(wrapper);
  });
}
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
    phase: "question",
    symptoms: [],        
    confidence: {}        
  };

  setActiveSession(sessionId);
  renderSessionList();
};

function setActiveSession(sessionId) {
  activeSessionId = sessionId;
  const session = sessions[sessionId];
  sessionInfo.innerText = `${session.label} • ${sessionId.slice(0, 8)}`;
  statusText.innerText = session.status;
  statusText.style.color =
    session.phase === "question" ? "#b91c1c" : "#166534";
  switch (session.phase) {
    case "question":
      userInput.disabled = false;
      sendBtn.disabled = false;
      userInput.placeholder = "Ask a question (e.g. Do you have fever?)";
      break;
    case "diagnosis":
      userInput.disabled = false;
      sendBtn.disabled = false;
      userInput.placeholder = "Type diagnosis: flu / migraine / food_poisoning";
      break;
    case "treatment":
      userInput.disabled = false;
      sendBtn.disabled = false;
      break;
    case "complete":
      userInput.disabled = true;
      sendBtn.disabled = true;
      userInput.placeholder = "Session completed";
      break;
  }
  renderChat();
  renderSessionList();
  updateMemory(session.symptoms);
  updateConfidenceBars(session.confidence);
}

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

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!activeSessionId) return;

  const message = userInput.value.trim();
  if (!message) return;
  userInput.value = "";

  const session = sessions[activeSessionId];

  session.chat.push({
    sender: "Doctor",
    text: message,
    cls: "user",
  });

  renderChat();
  showTypingIndicator(true);

  const res = await fetch("http://127.0.0.1:5000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: activeSessionId,
      message,
    }),
  });

  const data = await res.json();

  const minDelay = 900;
  const maxDelay = 2200;
  const charsPerMs = 18;
  const replyLength = (data.reply || "").length;

  const typingDelay = Math.min(
    maxDelay,
    Math.max(minDelay, replyLength * charsPerMs)
  );

  setTimeout(() => {
    showTypingIndicator(false);

    if (data.error) {
      session.chat.push({
        sender: "System",
        text: data.error,
        cls: "system",
      });
      renderChat();
      return;
    }

    if (data.reply) {
      session.chat.push({
        sender: "Patient",
        text: data.reply,
        cls: "patient",
      });
    }

    console.log("BACKEND RESPONSE:", data);

    if (data.symptoms_revealed) {
      session.symptoms = data.symptoms_revealed;
      updateMemory(session.symptoms);
    }

    if (data.disease_confidence) {
      session.confidence = data.disease_confidence;
      updateConfidenceBars(session.confidence);
    }

    if (data.next_action === "allow_diagnosis") {
      session.phase = "diagnosis";
      session.status = "Diagnosis can now be attempted";
    }

    if (data.evaluation) {
      session.chat.push({
        sender: "System",
        text: `Verdict: ${data.evaluation.verdict.toUpperCase()} — ${data.evaluation.reason}`,
        cls: "system",
      });

      if (data.evaluation.verdict === "correct") {
        session.phase = "treatment";
        session.status = "Diagnosis completed — prescribe treatment";
      }
    }

    if (data.treatment_verdict === "accepted") {
      session.chat.push({
        sender: "System",
        text: "Treatment accepted. Session completed.",
        cls: "system",
      });

      session.phase = "complete";
      session.status = "✅ Treatment completed";
    }

    setActiveSession(activeSessionId);
  }, typingDelay);
});

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
