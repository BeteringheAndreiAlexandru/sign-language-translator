// ---------- Camera ----------
const video = document.getElementById("video");
const btnStart = document.getElementById("btnStart");
const btnStop = document.getElementById("btnStop");
const btnToggleRecognize = document.getElementById("btnToggleRecognize");
const statusText = document.getElementById("statusText");
const statusDot = document.getElementById("statusDot");
const cameraBadge = document.getElementById("cameraBadge");
const fpsPill = document.getElementById("fpsPill");

let stream = null;
let recognizing = false;
let rafId = null;

// FPS calc
let lastT = performance.now();
let frames = 0;

function setCamUI(on){
  if(on){
    statusText.textContent = "Camera pornită";
    statusDot.style.background = "#22c55e";
    statusDot.style.boxShadow = "0 0 0 4px rgba(34,197,94,.18)";
    cameraBadge.textContent = "Live";
    btnStop.disabled = false;
    btnToggleRecognize.disabled = false;
  }else{
    statusText.textContent = "Camera oprită";
    statusDot.style.background = "#f59e0b";
    statusDot.style.boxShadow = "0 0 0 4px rgba(245,158,11,.15)";
    cameraBadge.textContent = "Idle";
    btnStop.disabled = true;
    btnToggleRecognize.disabled = true;
    btnToggleRecognize.textContent = "Start “Recunoaștere”";
  }
}

async function startCamera(){
  try{
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: {ideal:1280}, height: {ideal:720}, facingMode:"user" },
      audio: false
    });
    video.srcObject = stream;
    setCamUI(true);
  }catch(err){
    addBot("Nu am putut porni camera. Verifică permisiunile browserului.\n" + err.message);
  }
}

function stopCamera(){
  if(stream){
    stream.getTracks().forEach(t => t.stop());
    stream = null;
  }
  video.srcObject = null;
  setCamUI(false);
  stopRecognitionLoop();
}

btnStart.addEventListener("click", startCamera);
btnStop.addEventListener("click", stopCamera);

// ---------- Fake recognition loop (UI demo) ----------
const signOut = document.getElementById("signOut");
const confOut = document.getElementById("confOut");
const sentenceOut = document.getElementById("sentenceOut");

let sentence = "";
let lastEmit = 0;

const fakeLabels = ["HELLO", "YES", "NO", "THANK YOU", "PLEASE", "I", "YOU", "HELP", "WATER", "WHERE"];
function randomPick(arr){ return arr[Math.floor(Math.random()*arr.length)]; }
function randomConf(){ return (0.70 + Math.random()*0.29).toFixed(4); }

function startRecognitionLoop(){
  recognizing = true;
  btnToggleRecognize.textContent = "Stop “Recunoaștere”";
  lastT = performance.now(); frames = 0;
  loop();
}

function stopRecognitionLoop(){
  recognizing = false;
  if(rafId) cancelAnimationFrame(rafId);
  rafId = null;
  fpsPill.textContent = "FPS: --";
}

function loop(){
  rafId = requestAnimationFrame(loop);

  // fps update
  frames++;
  const now = performance.now();
  if(now - lastT >= 1000){
    const fps = Math.round(frames * 1000 / (now - lastT));
    fpsPill.textContent = "FPS: " + fps;
    lastT = now;
    frames = 0;
  }

  // every ~1.2s emit a fake prediction (ONLY as demo)
  if(!recognizing) return;
  if(now - lastEmit > 1200){
    lastEmit = now;

    // ---- AICI vei conecta ieșirea modelului real ----
    const label = randomPick(fakeLabels);
    const conf = randomConf();
    onPrediction(label, conf);
  }
}

btnToggleRecognize.addEventListener("click", () => {
  if(!stream){
    addBot("Pornește camera înainte să începi recunoașterea.");
    return;
  }
  if(!recognizing) startRecognitionLoop();
  else{
    stopRecognitionLoop();
    btnToggleRecognize.textContent = "Start “Recunoaștere”";
  }
});

function onPrediction(label, confidence){
  signOut.textContent = label;
  confOut.textContent = confidence;

  // build a sentence (foarte simplu)
  sentence = (sentence + " " + label).trim();
  sentenceOut.textContent = sentence;

  // exemplu: auto-send (dezactivat)
  // if(label === "HELLO") sendToChat("Detected: " + sentence);
}

// ---------- Chat UI (local demo bot) ----------
const messages = document.getElementById("messages");
const chatInput = document.getElementById("chatInput");
const btnSend = document.getElementById("btnSend");

function addMsg(text, who){
  const el = document.createElement("div");
  el.className = "msg " + who;
  el.textContent = text;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
}
function addUser(text){ addMsg(text, "user"); }
function addBot(text){ addMsg(text, "bot"); }

function demoBotReply(userText){
  // placeholder. Înlocuiește cu fetch("/api/chat", {method:"POST", body:...})
  const trimmed = userText.trim();
  if(!trimmed) return "Spune-mi ceva 🙂";
  if(trimmed.toLowerCase().includes("help")) return "Sigur. După ce conectezi backendul, pot răspunde real.";
  if(trimmed.toLowerCase().includes("camera")) return "Camera este în panoul din stânga. Pornește-o și apoi recunoașterea.";
  return "Am primit: “" + trimmed + "” (demo). Conectează backendul ca să ai răspunsuri reale.";
}

function sendToChat(text){
  const t = text.trim();
  if(!t) return;
  addUser(t);
  chatInput.value = "";

  // simulate latency
  btnSend.disabled = true;
  setTimeout(() => {
    addBot(demoBotReply(t));
    btnSend.disabled = false;
    chatInput.focus();
  }, 250);
}

btnSend.addEventListener("click", () => sendToChat(chatInput.value));
chatInput.addEventListener("keydown", (e) => {
  if(e.key === "Enter") sendToChat(chatInput.value);
});

// UX: click pe textul detectat → îl pune în input
sentenceOut.addEventListener("click", () => {
  const s = sentenceOut.textContent;
  if(s && s !== "—"){
    chatInput.value = s;
    chatInput.focus();
  }
});

// Init UI
setCamUI(false);
