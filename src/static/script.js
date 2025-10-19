const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");
const meta = document.getElementById("meta");
const clearBtn = document.getElementById("clear");
const pencilBtn = document.getElementById("pencil");
const eraserBtn = document.getElementById("eraser");
const brushSlider = document.getElementById("brushSlider");
const brushSizeLabel = document.getElementById("brushSizeLabel");
const sendBtn = document.getElementById("send");

ctx.fillStyle = "#FFFFFF";
ctx.fillRect(0, 0, canvas.width, canvas.height);

let drawing = false;
let lastX = 0, lastY = 0;
let sendTimer = null;
let currentTool = "pencil";
let brushSize = parseInt(brushSlider.value);

// Tool
function setTool(tool) {
  currentTool = tool;
  [pencilBtn, eraserBtn].forEach(b => b.classList.remove("active"));

  if (tool === "pencil") pencilBtn.classList.add("active");
  else eraserBtn.classList.add("active");

  if (tool === "pencil") canvas.style.cursor = "crosshair";
  else canvas.style.cursor = "cell";
}

// Size
brushSlider.addEventListener("input", e => {
  brushSize = parseInt(e.target.value);
  brushSizeLabel.textContent = `${brushSize} px`;
});

// Draw
function drawDot(x, y) {
  ctx.fillStyle = currentTool === "pencil" ? "#000000" : "#FFFFFF";

  const half = Math.floor(brushSize / 2);
  ctx.fillRect(x - half, y - half, brushSize, brushSize);
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

// Position
function getPos(e) {
  const rect = canvas.getBoundingClientRect();
  const clientX = e.touches ? e.touches[0].clientX : e.clientX;
  const clientY = e.touches ? e.touches[0].clientY : e.clientY;
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  const x = Math.floor((clientX - rect.left) * scaleX);
  const y = Math.floor((clientY - rect.top) * scaleY);
  return { x, y };
}

// Draw Events
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

// Send To Backend
sendBtn.addEventListener("click", () => sendToServer());

async function sendToServer() {
  const dataURL = canvas.toDataURL("image/png");
  const res = await fetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ imageDataURL: dataURL }),
  });
  const data = await res.json();
  meta.textContent = JSON.stringify(data, null, 2);
}

// Listeners
clearBtn.addEventListener("click", () => {
  ctx.fillStyle = "#FFFFFF";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
});

pencilBtn.addEventListener("click", () => setTool("pencil"));
eraserBtn.addEventListener("click", () => setTool("eraser"));

canvas.addEventListener("mousedown", startDraw);
canvas.addEventListener("mousemove", moveDraw);
canvas.addEventListener("mouseup", endDraw);
canvas.addEventListener("mouseleave", endDraw);
canvas.addEventListener("touchstart", startDraw, { passive: false });
canvas.addEventListener("touchmove", moveDraw, { passive: false });
canvas.addEventListener("touchend", endDraw, { passive: false });

setTool("pencil");

