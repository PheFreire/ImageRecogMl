const mlCanvas = document.getElementById("board");
const ctx = mlCanvas.getContext("2d");
const meta = document.getElementById("meta");
const clearBtn = document.getElementById("clear");
const pencilBtn = document.getElementById("pencil");
const eraserBtn = document.getElementById("eraser");
const eraseSlider = document.getElementById("eraseSlider");
const eraseSizeLabel = document.getElementById("eraseSizeLabel");
const sendBtn = document.getElementById("send");
const labelsDiv = document.getElementById("labels");
const sizeLabel = document.getElementById("sizeLabel");

ctx.fillStyle = "#FFFFFF";
ctx.fillRect(0, 0, mlCanvas.width, mlCanvas.height);

let drawing = false;
let lastX = 0, lastY = 0;
let sendTimer = null;
let currentTool = "pencil";
let eraseSize = parseInt(eraseSlider.value);

// ===== TOOL =====
function setTool(tool) {
  currentTool = tool;
  [pencilBtn, eraserBtn].forEach(b => b.classList.remove("active"));

  if (tool === "pencil") {
    pencilBtn.classList.add("active");
    mlCanvas.style.cursor = "crosshair";
    sizeLabel.style.display = "none";
  } else {
    eraserBtn.classList.add("active");
    mlCanvas.style.cursor = "cell";
    sizeLabel.style.display = "flex";
  }
}

// ===== SIZE =====
eraseSlider.addEventListener("input", e => {
  eraseSize = parseInt(e.target.value);
  eraseSizeLabel.textContent = `${eraseSize} px`;
});

// ===== DRAW =====
function drawDot(x, y) {
  ctx.fillStyle = currentTool === "pencil" ? "#000000" : "#FFFFFF";
  const size = currentTool === "pencil" ? 3 : eraseSize;
  const half = Math.floor(size / 2);
  ctx.fillRect(x - half, y - half, size, size);
}

function drawLine(x0, y0, x1, y1) {
  const dx = Math.abs(x1 - x0), sx = x0 < x1 ? 1 : -1;
  const dy = -Math.abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
  let err = dx + dy, e2;
  let x = x0, y = y0;
  while (true) {
    drawDot(x, y);
    if (x === x1 && y === y1) break;
    e2 = 2 * err;
    if (e2 >= dy) { err += dy; x += sx; }
    if (e2 <= dx) { err += dx; y += sy; }
  }
}

// ===== POSITION =====
function getPos(e) {
  const rect = mlCanvas.getBoundingClientRect();
  const clientX = e.touches ? e.touches[0].clientX : e.clientX;
  const clientY = e.touches ? e.touches[0].clientY : e.clientY;
  const scaleX = mlCanvas.width / rect.width;
  const scaleY = mlCanvas.height / rect.height;
  const x = Math.floor((clientX - rect.left) * scaleX);
  const y = Math.floor((clientY - rect.top) * scaleY);
  return { x, y };
}

// ===== DRAW EVENTS =====
function startDraw(e) {
  drawing = true;
  const { x, y } = getPos(e);
  lastX = x; lastY = y;
  drawDot(x, y);
  e.preventDefault();
}

function endDraw(e) {
  drawing = false;
  e.preventDefault();
}

function moveDraw(e) {
  if (!drawing) return;
  const { x, y } = getPos(e);
  drawLine(lastX, lastY, x, y);
  lastX = x; lastY = y;
  e.preventDefault();
}

// ===== CHECK IF EMPTY =====
// function isCanvasBlank() {
//   const pixelBuffer = new Uint32Array(
//     ctx.getImageData(0, 0, mlCanvas.width, mlCanvas.height).data.buffer
//   );
//   return !pixelBuffer.some(color => color !== 0);
// }

// ===== SEND TO BACKEND =====
async function sendToServer() {
  // if (isCanvasBlank()) {
  //   meta.textContent = "⚠️ O canvas está vazio. Desenhe algo antes de enviar.";
  //   meta.style.color = "red";
  //   return;
  // }

  const dataURL = mlCanvas.toDataURL("image/png");
  const res = await fetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ imageDataURL: dataURL }),
  });
  const data = await res.json();
  meta.textContent = JSON.stringify(data, null, 2);
  await updateLabelIndicators(data);
}

// ===== LABELS =====
function addNewLabel(labelName) {
  const div = document.createElement("div");
  div.classList.add("label-item");

  const ball = document.createElement("div");
  ball.classList.add("label-ball");
  ball.id = `label-${labelName}`;

  const text = document.createElement("span");
  text.textContent = labelName;

  div.appendChild(ball);
  div.appendChild(text);
  labelsDiv.appendChild(div);
}

async function loadLabels() {
  const res = await fetch("/labels", {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  const labels = await res.json();
  return labels;
}

async function renderLabels() {
  const labels = await loadLabels();
  labels.forEach(label => addNewLabel(label));
}

async function updateLabelIndicators(data) {
  const labels = await loadLabels();

  labels.forEach(label => {
    const el = document.getElementById(`label-${label}`);
    if (!el) return;
    el.style.backgroundColor = "#ccc";
    el.textContent = "";
  });

  const output = data.output || {};
  for (const [label, value] of Object.entries(output)) {
    const el = document.getElementById(`label-${label}`);
    if (!el) continue;
    const numeric = parseFloat(value.replace("%", ""));
    el.style.backgroundColor = label === data.predicted ? "#2ecc71" : "#888";
    el.textContent = numeric.toFixed(0) + "%";
  }
}

// ===== LISTENERS =====
sendBtn.addEventListener("click", async () => await sendToServer());

document.addEventListener("DOMContentLoaded", async () => {
  setTool("pencil");
  await renderLabels();
  sizeLabel.style.display = "none";
});

clearBtn.addEventListener("click", () => {
  ctx.fillStyle = "#FFFFFF";
  ctx.fillRect(0, 0, mlCanvas.width, mlCanvas.height);
});

pencilBtn.addEventListener("click", () => setTool("pencil"));
eraserBtn.addEventListener("click", () => setTool("eraser"));

mlCanvas.addEventListener("mousedown", startDraw);
mlCanvas.addEventListener("mousemove", moveDraw);
mlCanvas.addEventListener("mouseup", endDraw);
mlCanvas.addEventListener("mouseleave", endDraw);
mlCanvas.addEventListener("touchstart", startDraw, { passive: false });
mlCanvas.addEventListener("touchmove", moveDraw, { passive: false });
mlCanvas.addEventListener("touchend", endDraw, { passive: false });

setTool("pencil");

