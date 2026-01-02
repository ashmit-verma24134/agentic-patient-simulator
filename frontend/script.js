// const API_BASE = "http://127.0.0.1:5000";
const API_BASE = "https://founder-quiz-cologne-vector.trycloudflare.com";


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

//Helpers

function cleanPatientReply(text) {
  return text.replace(/^__EXPRESSIVE__/, "").trim();
}

function showTypingIndicator(show) {
  typingIndicator.style.display = show ? "block" : "none";
}

function updateMemory(symptoms = []) {
  memoryList.innerHTML = "";
  symptoms.forEach(s => {
    const li = document.createElement("li");
    li.innerText = `✔ ${s}`;
    memoryList.appendChild(li);
  });
}

function updateConfidenceBars(confidence = {}) {
  confidenceBars.innerHTML = "";
  Object.entries(confidence).forEach(([disease, percent]) => {
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

//Session management

createSessionBtn.onclick = async () => {
  const res = await fetch(`${API_BASE}/api/create_session`, { method: "POST" });
  const data = await res.json();

  sessions[data.session_id] = {
    label: `Patient ${patientCounter++}`,
    chat: [],
    status: "Diagnosis not allowed yet",
    phase: "question",
    symptoms: [],
    confidence: {}
  };

  setActiveSession(data.session_id);
  renderSessionList();
};

function setActiveSession(id) {
  activeSessionId = id;
  const s = sessions[id];

  sessionInfo.innerText = `${s.label} • ${id.slice(0, 8)}`;
  statusText.innerText = s.status;
  statusText.style.color = s.phase === "question" ? "#b91c1c" : "#166534";

  userInput.disabled = s.phase === "complete";
  sendBtn.disabled = s.phase === "complete";

  if (s.phase === "question") userInput.placeholder = "Ask a medical question";
  if (s.phase === "diagnosis") userInput.placeholder = "Type diagnosis";
  if (s.phase === "treatment") userInput.placeholder = "Prescribe treatment";
  if (s.phase === "complete") userInput.placeholder = "Session completed";

  renderChat();
  updateMemory(s.symptoms);
  updateConfidenceBars(s.confidence);
}

function renderSessionList() {
  sessionList.innerHTML = ""; // hard reset

  Object.entries(sessions).forEach(([id, session]) => {
    const div = document.createElement("div");

    div.classList.add("session-item");
    if (id === activeSessionId) {
      div.classList.add("active");
    }

    div.innerText = session.label;

    div.onclick = () => {
      setActiveSession(id);
      renderSessionList(); 
    };

    sessionList.appendChild(div);
  });
}


//Chat handler

chatForm.addEventListener("submit", async e => {
  e.preventDefault();
  if (!activeSessionId) return;

  const message = userInput.value.trim();
  if (!message) return;
  userInput.value = "";

  const session = sessions[activeSessionId];

  session.chat.push({ sender: "Doctor", text: message, cls: "user" });
  renderChat();
  showTypingIndicator(true);

  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: activeSessionId, message })
  });

  const data = await res.json();

  setTimeout(() => {
    showTypingIndicator(false);

//Verdicts

    if (data.verdict) {

      if (["correct", "incorrect", "blocked"].includes(data.verdict)) {
        session.chat.push({
          sender: "System",
          text: `Verdict: ${data.verdict.toUpperCase()} — ${data.reason || ""}`,
          cls: "system"
        });

        if (data.verdict === "correct") {
          session.phase = "treatment";
          session.status = "Diagnosis completed — prescribe treatment";
        }

        renderChat();
        setActiveSession(activeSessionId);
        return;
      }

      if (data.treatment_verdict === "accepted" || data.treatment_verdict === "rejected") {
        session.chat.push({
          sender: "Patient",
          text: cleanPatientReply(data.reply),
          cls: "patient"
        });

        if (data.treatment_verdict === "accepted") {
          session.chat.push({
            sender: "System",
            text: "Treatment accepted. Session completed.",
            cls: "system"
          });
          session.phase = "complete";
          session.status = "Treatment completed";
        } else {
          session.phase = "treatment";
          session.status = "Treatment rejected — try another treatment";
        }

        renderChat();
        setActiveSession(activeSessionId);
        return;
      }
    }

//Normal patient response

    if (data.reply) {
      session.chat.push({
        sender: "Patient",
        text: cleanPatientReply(data.reply),
        cls: "patient"
      });
    }

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

    renderChat();
    setActiveSession(activeSessionId);
  }, 900);
});

//Chatrender

function renderChat() {
  chatBox.innerHTML = "";
  sessions[activeSessionId]?.chat.forEach(m => {
    const div = document.createElement("div");
    div.className = "message " + m.cls;
    div.innerText = `${m.sender}: ${m.text}`;
    chatBox.appendChild(div);
  });
  chatBox.scrollTop = chatBox.scrollHeight;
}
