// Configurare WebSocket 
const ws = new WebSocket("ws://localhost:8765");

ws.onopen = () => {
  console.log("Conectat la Backend-ul Python!");
  addBot("Sistem conectat la serverul AI.");
};

ws.onmessage = (event) => {
  
  const data = JSON.parse(event.data);
  
  if (data.status === "success") {
    onPrediction(data.label, data.confidence);
  }
};

ws.onerror = (error) => {
  console.error("Eroare WebSocket: ", error);
  addBot("Eroare de conexiune cu serverul.");
};


const hiddenCanvas = document.createElement("canvas");
const hiddenCtx = hiddenCanvas.getContext("2d", { willReadFrequently: true });


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
    statusText.textContent = "Camera pornita";
    statusDot.style.background = "#22c55e";
    statusDot.style.boxShadow = "0 0 0 4px rgba(34,197,94,.18)";
    cameraBadge.textContent = "Live";
    btnStop.disabled = false;
    btnToggleRecognize.disabled = false;
  }else{
    statusText.textContent = "Camera oprita";
    statusDot.style.background = "#f59e0b";
    statusDot.style.boxShadow = "0 0 0 4px rgba(245,158,11,.15)";
    cameraBadge.textContent = "Idle";
    btnStop.disabled = true;
    btnToggleRecognize.disabled = true;
    btnToggleRecognize.textContent = "Start “Recunoastere”";
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


const signOut = document.getElementById("signOut");
const confOut = document.getElementById("confOut");
const sentenceOut = document.getElementById("sentenceOut");

let sentence = "";
let lastEmit = 0;

function startRecognitionLoop(){
  recognizing = true;
  btnToggleRecognize.textContent = "Stop “Recunoastere”";
  lastT = performance.now(); 
  frames = 0;
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


  frames++;
  const now = performance.now();
  if(now - lastT >= 1000){
    const fps = Math.round(frames * 1000 / (now - lastT));
    fpsPill.textContent = "FPS: " + fps;
    lastT = now;
    frames = 0;
  }

  if(!recognizing) return;
  
  
  if(now - lastEmit > 300){
    lastEmit = now;

    
    if (video.readyState === video.HAVE_ENOUGH_DATA) {
        hiddenCanvas.width = video.videoWidth;
        hiddenCanvas.height = video.videoHeight;

        hiddenCtx.drawImage(video, 0, 0, hiddenCanvas.width, hiddenCanvas.height);
        
        const frameData = hiddenCanvas.toDataURL("image/jpeg", 0.5);
        
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(frameData);
        }
    }
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


  sentence = (sentence + " " + label).trim();
  sentenceOut.textContent = sentence;
}


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
  const trimmed = userText.trim();
  if(!trimmed) return "Spune-mi ceva ";
  if(trimmed.toLowerCase().includes("help")) return "Sistemul este acum pregătit să primească date reale de la serverul Python.";
  return "Am primit: “" + trimmed + "”. Poți folosi semnele recunoscute pentru a scrie aici!";
}

function sendToChat(text){
  const t = text.trim();
  if(!t) return;
  addUser(t);
  chatInput.value = "";

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

sentenceOut.addEventListener("click", () => {
  const s = sentenceOut.textContent;
  if(s && s !== "—"){
    chatInput.value = s;
    chatInput.focus();
  }
});


setCamUI(false);