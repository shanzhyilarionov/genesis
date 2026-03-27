import os
import socket
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

_server_started = False
_browser_opened = False
_port = None

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Genesis</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <canvas id="world"></canvas>
  <script src="app.js"></script>
</body>
</html>
"""

STYLE_CSS = """:root {
  --bg: #ffffff;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #000000;
  }
}

html, body {
  margin: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: var(--bg);
}

canvas {
  display: block;
  width: 100vw;
  height: 100vh;
  background: var(--bg);
}
"""

APP_JS = """const canvas = document.getElementById("world");
const ctx = canvas.getContext("2d", { alpha: false });

const themeQuery = window.matchMedia("(prefers-color-scheme: dark)");

const COLORS = {
  backgroundLight: "#ffffff",
  backgroundDark: "#000000",
  food: "#808080",
  speciesA: "#33cc66",
  speciesB: "#ff4d4d"
};

function resizeCanvas() {
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.floor(window.innerWidth * dpr);
  canvas.height = Math.floor(window.innerHeight * dpr);
  canvas.style.width = `${window.innerWidth}px`;
  canvas.style.height = `${window.innerHeight}px`;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.imageSmoothingEnabled = false;
}

function getBackgroundColor() {
  return themeQuery.matches ? COLORS.backgroundDark : COLORS.backgroundLight;
}

function drawFrame(frame) {
  const viewWidth = window.innerWidth;
  const viewHeight = window.innerHeight;

  ctx.fillStyle = getBackgroundColor();
  ctx.fillRect(0, 0, viewWidth, viewHeight);

  const cellSize = Math.max(
    viewWidth / frame.width,
    viewHeight / frame.height
  );

  const worldDrawWidth = frame.width * cellSize;
  const worldDrawHeight = frame.height * cellSize;

  const offsetX = (viewWidth - worldDrawWidth) / 2;
  const offsetY = (viewHeight - worldDrawHeight) / 2;

  for (let y = 0; y < frame.height; y++) {
    for (let x = 0; x < frame.width; x++) {
      const value = frame.cells[y][x];
      if (value === 0) continue;

      if (value === 1) {
        ctx.fillStyle = COLORS.food;
      } else if (value === 2) {
        ctx.fillStyle = COLORS.speciesA;
      } else if (value === 3) {
        ctx.fillStyle = COLORS.speciesB;
      }

      ctx.fillRect(
        offsetX + x * cellSize,
        offsetY + y * cellSize,
        cellSize,
        cellSize
      );
    }
  }
}

async function fetchState() {
  try {
    const response = await fetch(`state.json?t=${Date.now()}`, {
      cache: "no-store"
    });
    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  }
}

async function loop() {
  const frame = await fetchState();
  if (frame) {
    drawFrame(frame);
  }
  setTimeout(loop, 50);
}

resizeCanvas();
window.addEventListener("resize", resizeCanvas);
loop();
"""

class ReusableTCPServer(TCPServer):
    allow_reuse_address = True

def _get_root_dir():
    return os.path.dirname(os.path.dirname(__file__))

def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

def ensure_web_assets():
    root_dir = _get_root_dir()
    web_dir = os.path.join(root_dir, "web")
    os.makedirs(web_dir, exist_ok=True)

    files = {
        "index.html": INDEX_HTML,
        "style.css": STYLE_CSS,
        "app.js": APP_JS,
    }

    for name, content in files.items():
        path = os.path.join(web_dir, name)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    state_path = os.path.join(web_dir, "state.json")
    if not os.path.exists(state_path):
        with open(state_path, "w", encoding="utf-8") as f:
            f.write('{"tick":0,"width":1,"height":1,"cells":[[0]]}')

def start_web_server():
    global _server_started, _port

    if _server_started:
        return

    root_dir = _get_root_dir()
    web_dir = os.path.join(root_dir, "web")
    _port = _find_free_port()

    handler = partial(SimpleHTTPRequestHandler, directory=web_dir)

    def serve():
        with ReusableTCPServer(("127.0.0.1", _port), handler) as httpd:
            httpd.serve_forever()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    _server_started = True

def open_browser():
    global _browser_opened

    if _browser_opened:
        return

    if _port is None:
        return

    _browser_opened = True
    url = f"http://127.0.0.1:{_port}"
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()