"""Interactive Three.js particle-morph 3D landing page for SafePay Control Panel."""

import streamlit as st
import streamlit.components.v1 as components


LANDING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<style>
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  html, body {
    width: 100%;
    height: 640px;
    overflow: hidden;
    background: #04051a;
    color: #f8fafc;
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    user-select: none;
    -webkit-user-select: none;
  }

  #scene-wrap {
    position: relative;
    width: 100%;
    height: 640px;
    background:
      radial-gradient(circle at 22% 24%, rgba(0, 245, 212, 0.14) 0%, transparent 44%),
      radial-gradient(circle at 78% 76%, rgba(241, 91, 181, 0.13) 0%, transparent 46%),
      radial-gradient(circle at 52% 48%, rgba(155, 93, 229, 0.10) 0%, transparent 55%),
      #04051a;
    border: 1px solid rgba(0, 245, 212, 0.22);
    border-radius: 20px;
    overflow: hidden;
    touch-action: pan-y;
  }

  canvas#particle-canvas {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    display: block;
    touch-action: pan-y;
    cursor: grab;
  }

  canvas#particle-canvas:active {
    cursor: grabbing;
  }

  .hud-top {
    position: absolute;
    top: 22px;
    left: 20px;
    right: 20px;
    z-index: 3;
    text-align: center;
    pointer-events: none;
  }

  .glitch-title {
    display: inline-block;
    font-size: clamp(1.45rem, 3.6vw, 2.55rem);
    font-weight: 850;
    letter-spacing: 0.04em;
    color: #f8fafc;
    text-shadow:
      0 0 18px rgba(0, 245, 212, 0.35),
      0 0 32px rgba(155, 93, 229, 0.25);
    animation: rgbGlitch 4.4s infinite;
  }

  @keyframes rgbGlitch {
    0%, 88%, 100% {
      transform: translate(0, 0);
      text-shadow:
        0 0 18px rgba(0, 245, 212, 0.35),
        0 0 32px rgba(155, 93, 229, 0.25);
    }
    89% {
      transform: translate(-2px, 0);
      text-shadow:
        3px 0 0 rgba(0, 245, 212, 0.85),
        -3px 0 0 rgba(241, 91, 181, 0.85);
    }
    90.5% {
      transform: translate(2px, -1px);
      text-shadow:
        -3px 1px 0 rgba(0, 245, 212, 0.9),
        3px -1px 0 rgba(241, 91, 181, 0.9);
    }
    92% {
      transform: translate(-1px, 1px);
      text-shadow:
        2px 0 0 rgba(155, 93, 229, 0.9),
        -2px 0 0 rgba(0, 245, 212, 0.9);
    }
    93.5% {
      transform: translate(0, 0);
      text-shadow:
        0 0 18px rgba(0, 245, 212, 0.35),
        0 0 32px rgba(155, 93, 229, 0.25);
    }
  }

  .tagline {
    margin-top: 8px;
    font-size: clamp(0.88rem, 1.8vw, 1.08rem);
    font-weight: 650;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.55rem;
  }

  .tag-word {
    color: rgba(203, 213, 225, 0.32);
    transition: color 0.45s ease, text-shadow 0.45s ease, transform 0.45s ease;
  }

  .tag-word.active-cyan {
    color: #00f5d4;
    text-shadow: 0 0 14px rgba(0, 245, 212, 0.85);
    transform: translateY(-1px);
  }

  .tag-word.active-purple {
    color: #c084fc;
    text-shadow: 0 0 14px rgba(155, 93, 229, 0.9);
    transform: translateY(-1px);
  }

  .tag-word.active-pink {
    color: #f15bb5;
    text-shadow: 0 0 14px rgba(241, 91, 181, 0.85);
    transform: translateY(-1px);
  }

  .hud-bottom {
    position: absolute;
    bottom: 18px;
    left: 20px;
    right: 20px;
    z-index: 3;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    pointer-events: none;
  }

  .access-granted {
    display: none;
    padding: 8px 20px;
    border-radius: 999px;
    background: rgba(0, 245, 212, 0.16);
    border: 1px solid rgba(0, 245, 212, 0.72);
    color: #00f5d4;
    font-size: 0.95rem;
    font-weight: 750;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    box-shadow: 0 0 26px rgba(0, 245, 212, 0.45);
    animation: fadePulse 0.6s ease both;
  }

  .access-granted.show {
    display: inline-block;
  }

  @keyframes fadePulse {
    from { opacity: 0; transform: scale(0.92); }
    to { opacity: 1; transform: scale(1); }
  }

  .warp-trigger {
    pointer-events: auto;
    cursor: pointer;
    padding: 10px 22px;
    border-radius: 999px;
    border: 1px solid rgba(0, 245, 212, 0.55);
    background: rgba(4, 15, 36, 0.68);
    color: #00f5d4;
    font-size: 0.84rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    backdrop-filter: blur(8px);
    box-shadow: 0 0 18px rgba(0, 245, 212, 0.22);
    transition: all 0.25s ease;
  }

  .warp-trigger:hover {
    background: rgba(0, 245, 212, 0.18);
    box-shadow: 0 0 28px rgba(0, 245, 212, 0.45);
    transform: translateY(-1px);
  }

  .hint-note {
    font-size: 0.74rem;
    letter-spacing: 0.06em;
    color: rgba(148, 163, 184, 0.72);
    text-transform: uppercase;
  }
</style>
</head>
<body>
<div id="scene-wrap">
  <canvas id="particle-canvas"></canvas>

  <div class="hud-top">
    <div class="glitch-title">SafePay Control Panel</div>
    <div class="tagline">
      <span id="w-secure" class="tag-word">Secure.</span>
      <span id="w-instant" class="tag-word">Instant.</span>
      <span id="w-smart" class="tag-word">Smart Payments.</span>
    </div>
  </div>

  <div class="hud-bottom">
    <div id="access-msg" class="access-granted">Access granted</div>
    <button id="warp-btn" class="warp-trigger" type="button">Launch Control Panel Warp</button>
    <div class="hint-note">Move pointer to repel &bull; Tap or click for burst</div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
  const wrap = document.getElementById("scene-wrap");
  const canvas = document.getElementById("particle-canvas");
  const wSecure = document.getElementById("w-secure");
  const wInstant = document.getElementById("w-instant");
  const wSmart = document.getElementById("w-smart");
  const accessMsg = document.getElementById("access-msg");
  const warpBtn = document.getElementById("warp-btn");

  const PARTICLE_COUNT = 5400;
  const RING_COUNT = 420;
  const STAR_COUNT = 700;
  const SHAPE_HOLD_TIMES = [2.6, 2.6, 2.6, 2.6, 3.6];

  const HEX_CYAN = [0, 245 / 255, 212 / 255];
  const HEX_PURPLE = [155 / 255, 93 / 255, 229 / 255];
  const HEX_PINK = [241 / 255, 91 / 255, 181 / 255];

  function clampVal(v, lo, hi) {
    return Math.max(lo, Math.min(hi, v));
  }

  function updateTaglineHighlight(shapeIdx) {
    wSecure.className = "tag-word";
    wInstant.className = "tag-word";
    wSmart.className = "tag-word";
    if (shapeIdx === 0) {
      wSecure.classList.add("active-cyan");
    } else if (shapeIdx === 1) {
      wInstant.classList.add("active-purple");
    } else if (shapeIdx === 2) {
      wSmart.classList.add("active-pink");
    } else {
      wSecure.classList.add("active-cyan");
      wInstant.classList.add("active-purple");
      wSmart.classList.add("active-pink");
    }
  }

  let redirectTriggered = false;
  function openControlPanel() {
    if (redirectTriggered) return;
    redirectTriggered = true;
    try {
      const parentDoc = window.parent && window.parent.document;
      if (parentDoc) {
        const buttons = parentDoc.querySelectorAll("button");
        for (let i = 0; i < buttons.length; i++) {
          if ((buttons[i].innerText || "").trim() === "Enter Control Panel") {
            buttons[i].click();
            return;
          }
        }
      }
    } catch (e) {}
    try {
      const url = new URL(window.top.location.href);
      url.searchParams.set("enter", "1");
      window.top.location.href = url.toString();
    } catch (e) {}
  }

  // ---------------------------------------------------------------
  // Shape sampling on hidden 512x256 canvas
  // ---------------------------------------------------------------
  const sampleCanvas = document.createElement("canvas");
  sampleCanvas.width = 512;
  sampleCanvas.height = 256;
  const sctx = sampleCanvas.getContext("2d");

  function sampleCurrentShape(worldWidth, worldHeight, zJitter) {
    const img = sctx.getImageData(0, 0, 512, 256).data;
    const valid = [];
    for (let y = 0; y < 256; y++) {
      for (let x = 0; x < 512; x++) {
        if (img[(y * 512 + x) * 4 + 3] > 128) valid.push(x, y);
      }
    }
    const totalPixels = valid.length / 2;
    const out = new Float32Array(PARTICLE_COUNT * 3);
    if (totalPixels === 0) return out;

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const idx = Math.floor(Math.random() * totalPixels) * 2;
      out[i * 3 + 0] = ((valid[idx] / 512) - 0.5) * worldWidth;
      out[i * 3 + 1] = (0.5 - (valid[idx + 1] / 256)) * worldHeight;
      out[i * 3 + 2] = (Math.random() - 0.5) * zJitter;
    }
    return out;
  }

  function drawRoundedRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }

  function buildShapes() {
    const shapes = [];

    // 0: Padlock
    sctx.clearRect(0, 0, 512, 256);
    sctx.globalCompositeOperation = "source-over";
    sctx.fillStyle = "#ffffff";
    sctx.strokeStyle = "#ffffff";
    sctx.lineWidth = 18;
    sctx.beginPath();
    sctx.arc(256, 98, 42, Math.PI, 0, false);
    sctx.stroke();
    sctx.beginPath();
    sctx.moveTo(214, 98); sctx.lineTo(214, 120);
    sctx.moveTo(298, 98); sctx.lineTo(298, 120);
    sctx.stroke();
    drawRoundedRect(sctx, 188, 114, 136, 102, 18);
    sctx.fill();
    sctx.globalCompositeOperation = "destination-out";
    sctx.beginPath();
    sctx.arc(256, 155, 14, 0, Math.PI * 2);
    sctx.fill();
    sctx.fillRect(249, 159, 14, 30);
    sctx.globalCompositeOperation = "source-over";
    shapes.push(sampleCurrentShape(5.6, 2.8, 0.35));

    // 1: Lightning bolt
    sctx.clearRect(0, 0, 512, 256);
    sctx.fillStyle = "#ffffff";
    sctx.beginPath();
    sctx.moveTo(280, 22);
    sctx.lineTo(188, 140);
    sctx.lineTo(248, 140);
    sctx.lineTo(222, 236);
    sctx.lineTo(328, 110);
    sctx.lineTo(266, 110);
    sctx.closePath();
    sctx.fill();
    shapes.push(sampleCurrentShape(5.6, 2.8, 0.35));

    // 2: Payment card (outline, stripe, chip, contactless arcs)
    sctx.clearRect(0, 0, 512, 256);
    sctx.strokeStyle = "#ffffff";
    sctx.fillStyle = "#ffffff";
    sctx.lineWidth = 12;
    drawRoundedRect(sctx, 124, 44, 264, 168, 20);
    sctx.stroke();
    sctx.fillRect(130, 74, 252, 26);
    drawRoundedRect(sctx, 154, 120, 46, 34, 6);
    sctx.fill();
    for (let r = 14; r <= 36; r += 11) {
      sctx.lineWidth = 6;
      sctx.beginPath();
      sctx.arc(332, 138, r, -0.7, 0.7);
      sctx.stroke();
    }
    shapes.push(sampleCurrentShape(6.2, 3.1, 0.32));

    // 3: Shield with checkmark cut-out using destination-out
    sctx.clearRect(0, 0, 512, 256);
    sctx.globalCompositeOperation = "source-over";
    sctx.fillStyle = "#ffffff";
    sctx.beginPath();
    sctx.moveTo(256, 24);
    sctx.lineTo(346, 58);
    sctx.lineTo(338, 136);
    sctx.quadraticCurveTo(326, 198, 256, 232);
    sctx.quadraticCurveTo(186, 198, 174, 136);
    sctx.lineTo(166, 58);
    sctx.closePath();
    sctx.fill();
    sctx.globalCompositeOperation = "destination-out";
    sctx.strokeStyle = "#000000";
    sctx.lineWidth = 20;
    sctx.lineCap = "round";
    sctx.lineJoin = "round";
    sctx.beginPath();
    sctx.moveTo(212, 128);
    sctx.lineTo(244, 160);
    sctx.lineTo(304, 94);
    sctx.stroke();
    sctx.globalCompositeOperation = "source-over";
    shapes.push(sampleCurrentShape(5.8, 2.9, 0.36));

    // 4: Bold sans-serif "SAFEPAY"
    sctx.clearRect(0, 0, 512, 256);
    sctx.fillStyle = "#ffffff";
    sctx.font = "900 88px Inter, Segoe UI, Arial, sans-serif";
    sctx.textAlign = "center";
    sctx.textBaseline = "middle";
    sctx.fillText("SAFEPAY", 256, 130);
    shapes.push(sampleCurrentShape(6.9, 3.45, 0.26));

    return shapes;
  }

  const shapeTargets = buildShapes();

  function colorFromX(tx) {
    const t = clampVal((tx + 3.4) / 6.8, 0, 1);
    if (t < 0.5) {
      const k = t * 2;
      return [
        HEX_CYAN[0] + (HEX_PURPLE[0] - HEX_CYAN[0]) * k,
        HEX_CYAN[1] + (HEX_PURPLE[1] - HEX_CYAN[1]) * k,
        HEX_CYAN[2] + (HEX_PURPLE[2] - HEX_CYAN[2]) * k
      ];
    }
    const k = (t - 0.5) * 2;
    return [
      HEX_PURPLE[0] + (HEX_PINK[0] - HEX_PURPLE[0]) * k,
      HEX_PURPLE[1] + (HEX_PINK[1] - HEX_PURPLE[1]) * k,
      HEX_PURPLE[2] + (HEX_PINK[2] - HEX_PURPLE[2]) * k
    ];
  }

  // ---------------------------------------------------------------
  // Primary Engine: Three.js r128 WebGL
  // ---------------------------------------------------------------
  function startThreeEngine() {
    if (typeof THREE === "undefined") return false;

    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        antialias: true,
        alpha: false,
        powerPreference: "high-performance"
      });
      if (!renderer.getContext()) return false;
    } catch (e) {
      return false;
    }

    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setClearColor(0x04051a, 1);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x04051a);

    const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 160);
    let baseCamZ = 7.4;
    let targetFov = 50;
    let lastW = 0;
    let lastH = 0;

    function updateSizing() {
      const w = Math.max(wrap.clientWidth || window.innerWidth, 300);
      const h = Math.max(wrap.clientHeight || 640, 320);
      if (w === lastW && h === lastH) return;
      lastW = w;
      lastH = h;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      baseCamZ = camera.aspect < 1.0
        ? Math.max(8.4, 6.9 / Math.max(camera.aspect, 0.45))
        : Math.max(6.8, 7.6 / Math.min(camera.aspect, 1.45));
      camera.updateProjectionMatrix();
    }
    window.addEventListener("resize", updateSizing);
    if (typeof ResizeObserver !== "undefined") {
      new ResizeObserver(updateSizing).observe(wrap);
    }
    updateSizing();
    camera.position.set(0, 0, baseCamZ);

    // Radial-gradient canvas sprite
    const sc = document.createElement("canvas");
    sc.width = 64;
    sc.height = 64;
    const sSpriteCtx = sc.getContext("2d");
    const grad = sSpriteCtx.createRadialGradient(32, 32, 0, 32, 32, 32);
    grad.addColorStop(0.0, "rgba(255,255,255,1)");
    grad.addColorStop(0.32, "rgba(255,255,255,0.92)");
    grad.addColorStop(0.7, "rgba(255,255,255,0.28)");
    grad.addColorStop(1.0, "rgba(255,255,255,0)");
    sSpriteCtx.fillStyle = grad;
    sSpriteCtx.fillRect(0, 0, 64, 64);
    const spriteTex = new THREE.CanvasTexture(sc);
    spriteTex.needsUpdate = true;

    const particleGroup = new THREE.Group();
    scene.add(particleGroup);

    const positions = new Float32Array(PARTICLE_COUNT * 3);
    const velocities = new Float32Array(PARTICLE_COUNT * 3);
    const colors = new Float32Array(PARTICLE_COUNT * 3);
    const targetPositions = new Float32Array(PARTICLE_COUNT * 3);
    const targetColors = new Float32Array(PARTICLE_COUNT * 3);

    function setTargetShape(shapeIdx, applyVortex) {
      const src = shapeTargets[shapeIdx];
      for (let i = 0; i < PARTICLE_COUNT; i++) {
        const ix = i * 3;
        const tx = src[ix + 0];
        targetPositions[ix + 0] = tx;
        targetPositions[ix + 1] = src[ix + 1];
        targetPositions[ix + 2] = src[ix + 2];

        const c = colorFromX(tx);
        targetColors[ix + 0] = c[0];
        targetColors[ix + 1] = c[1];
        targetColors[ix + 2] = c[2];

        if (applyVortex) {
          const px = positions[ix + 0];
          const py = positions[ix + 1];
          const pz = positions[ix + 2];
          velocities[ix + 0] += -py * 2.6 + (Math.random() - 0.5) * 3.8;
          velocities[ix + 1] += px * 2.6 + (Math.random() - 0.5) * 3.8;
          velocities[ix + 2] += (Math.random() - 0.5) * 4.2 - pz * 0.4;
        }
      }
      updateTaglineHighlight(shapeIdx);
    }

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const ix = i * 3;
      positions[ix + 0] = (Math.random() - 0.5) * 10;
      positions[ix + 1] = (Math.random() - 0.5) * 6;
      positions[ix + 2] = (Math.random() - 0.5) * 6;
      colors[ix + 0] = HEX_CYAN[0];
      colors[ix + 1] = HEX_CYAN[1];
      colors[ix + 2] = HEX_CYAN[2];
    }
    setTargetShape(0, false);

    const mainGeo = new THREE.BufferGeometry();
    mainGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    mainGeo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    const mainMat = new THREE.PointsMaterial({
      size: 0.145,
      map: spriteTex,
      vertexColors: true,
      transparent: true,
      opacity: 0.96,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true
    });
    particleGroup.add(new THREE.Points(mainGeo, mainMat));

    // 420-particle alternating cyan/pink tilted rotating ring
    const ringPos = new Float32Array(RING_COUNT * 3);
    const ringCol = new Float32Array(RING_COUNT * 3);
    for (let i = 0; i < RING_COUNT; i++) {
      const a = (i / RING_COUNT) * Math.PI * 2;
      const rad = 3.55 + (Math.random() - 0.5) * 0.14;
      ringPos[i * 3 + 0] = Math.cos(a) * rad;
      ringPos[i * 3 + 1] = (Math.random() - 0.5) * 0.08;
      ringPos[i * 3 + 2] = Math.sin(a) * rad;
      const c = (i % 2 === 0) ? HEX_CYAN : HEX_PINK;
      ringCol[i * 3 + 0] = c[0];
      ringCol[i * 3 + 1] = c[1];
      ringCol[i * 3 + 2] = c[2];
    }
    const ringGeo = new THREE.BufferGeometry();
    ringGeo.setAttribute("position", new THREE.BufferAttribute(ringPos, 3));
    ringGeo.setAttribute("color", new THREE.BufferAttribute(ringCol, 3));
    const ringPoints = new THREE.Points(ringGeo, new THREE.PointsMaterial({
      size: 0.12,
      map: spriteTex,
      vertexColors: true,
      transparent: true,
      opacity: 0.78,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    }));
    ringPoints.rotation.x = 1.15;
    ringPoints.rotation.z = -0.35;
    particleGroup.add(ringPoints);

    // ~700-point starfield
    const starPos = new Float32Array(STAR_COUNT * 3);
    const starCol = new Float32Array(STAR_COUNT * 3);
    const starPalette = [HEX_CYAN, HEX_PURPLE, HEX_PINK, [0.9, 0.95, 1.0]];
    for (let i = 0; i < STAR_COUNT; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 18 + Math.random() * 24;
      starPos[i * 3 + 0] = r * Math.sin(phi) * Math.cos(theta);
      starPos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      starPos[i * 3 + 2] = r * Math.cos(phi) - 6;
      const c = starPalette[i % starPalette.length];
      starCol[i * 3 + 0] = c[0];
      starCol[i * 3 + 1] = c[1];
      starCol[i * 3 + 2] = c[2];
    }
    const starGeo = new THREE.BufferGeometry();
    starGeo.setAttribute("position", new THREE.BufferAttribute(starPos, 3));
    starGeo.setAttribute("color", new THREE.BufferAttribute(starCol, 3));
    const stars = new THREE.Points(starGeo, new THREE.PointsMaterial({
      size: 0.14,
      map: spriteTex,
      vertexColors: true,
      transparent: true,
      opacity: 0.65,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    }));
    scene.add(stars);

    const pointerNDC = new THREE.Vector2(0, 0);
    const pointerActive = { active: false };
    const raycaster = new THREE.Raycaster();
    const planeZ0 = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
    const worldHit = new THREE.Vector3();
    const localHit = new THREE.Vector3();

    function updatePointer(clientX, clientY) {
      const rect = canvas.getBoundingClientRect();
      if (rect.width <= 0 || rect.height <= 0) return;
      pointerNDC.x = ((clientX - rect.left) / rect.width) * 2 - 1;
      pointerNDC.y = -((clientY - rect.top) / rect.height) * 2 + 1;
      pointerActive.active = true;
    }

    canvas.addEventListener("pointermove", (e) => updatePointer(e.clientX, e.clientY), { passive: true });
    canvas.addEventListener("pointerleave", () => { pointerActive.active = false; }, { passive: true });
    canvas.addEventListener("pointerdown", (e) => {
      updatePointer(e.clientX, e.clientY);
      raycaster.setFromCamera(pointerNDC, camera);
      if (raycaster.ray.intersectPlane(planeZ0, worldHit)) {
        particleGroup.updateMatrixWorld();
        localHit.copy(worldHit);
        particleGroup.worldToLocal(localHit);
        for (let i = 0; i < PARTICLE_COUNT; i++) {
          const ix = i * 3;
          const dx = positions[ix + 0] - localHit.x;
          const dy = positions[ix + 1] - localHit.y;
          const dz = positions[ix + 2] - localHit.z;
          const dist = Math.sqrt(dx * dx + dy * dy + dz * dz) + 0.001;
          const boost = Math.max(0.8, 3.8 / (dist + 0.45));
          velocities[ix + 0] += (dx / dist) * boost + (Math.random() - 0.5) * 1.1;
          velocities[ix + 1] += (dy / dist) * boost + (Math.random() - 0.5) * 1.1;
          velocities[ix + 2] += (dz / dist) * boost + (Math.random() - 0.5) * 1.4;
        }
      }
    }, { passive: true });

    let warpPhase = "idle";
    let warpElapsed = 0;

    warpBtn.addEventListener("click", () => {
      if (warpPhase !== "idle") return;
      warpPhase = "fling";
      warpElapsed = 0;
      warpBtn.style.opacity = "0.35";
      warpBtn.style.pointerEvents = "none";
      setTargetShape(4, false);
      for (let i = 0; i < PARTICLE_COUNT; i++) {
        const ix = i * 3;
        const px = positions[ix + 0];
        const py = positions[ix + 1];
        const rad = Math.hypot(px, py) + 0.1;
        velocities[ix + 0] = (px / rad) * (5 + Math.random() * 6);
        velocities[ix + 1] = (py / rad) * (5 + Math.random() * 6);
        velocities[ix + 2] = 10 + Math.random() * 14;
      }
    });

    let currentShapeIdx = 0;
    let shapeTimer = 0;
    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);
      updateSizing();
      const dt = Math.min(clock.getDelta(), 0.05);
      const elapsed = clock.elapsedTime;

      if (warpPhase === "idle") {
        shapeTimer += dt;
        if (shapeTimer >= SHAPE_HOLD_TIMES[currentShapeIdx]) {
          shapeTimer = 0;
          currentShapeIdx = (currentShapeIdx + 1) % shapeTargets.length;
          setTargetShape(currentShapeIdx, true);
        }
      }

      particleGroup.rotation.y = Math.sin(elapsed * 0.42) * 0.14;
      particleGroup.rotation.x = Math.cos(elapsed * 0.31) * 0.08;
      ringPoints.rotation.y += dt * 0.45;
      stars.rotation.y += dt * 0.018;

      const px = pointerActive.active ? pointerNDC.x * 0.55 : 0;
      const py = pointerActive.active ? pointerNDC.y * 0.35 : 0;
      camera.position.x += (px - camera.position.x) * Math.min(1, dt * 4.0);
      camera.position.y += (py - camera.position.y) * Math.min(1, dt * 4.0);
      camera.position.z += (baseCamZ - camera.position.z) * Math.min(1, dt * 4.0);
      camera.lookAt(0, 0, 0);

      let activeSpring = 14.0;
      const DAMPING = 6.0;

      if (warpPhase === "fling") {
        warpElapsed += dt;
        activeSpring = 0.0;
        targetFov = 105;
        if (warpElapsed >= 1.4) {
          for (let i = 0; i < PARTICLE_COUNT; i++) {
            const ix = i * 3;
            positions[ix + 0] = (Math.random() - 0.5) * 18;
            positions[ix + 1] = (Math.random() - 0.5) * 10;
            positions[ix + 2] = -30 - Math.random() * 20;
            velocities[ix + 0] *= 0.15;
            velocities[ix + 1] *= 0.15;
            velocities[ix + 2] = 6 + Math.random() * 6;
          }
          warpPhase = "reform";
          warpElapsed = 0;
        }
      } else if (warpPhase === "reform") {
        warpElapsed += dt;
        targetFov = 50;
        activeSpring = Math.min(18.0, 2.5 + warpElapsed * 11.0);
        if (warpElapsed >= 1.15) {
          warpPhase = "granted";
          warpElapsed = 0;
          accessMsg.classList.add("show");
        }
      } else if (warpPhase === "granted") {
        warpElapsed += dt;
        targetFov = 50;
        activeSpring = 15.0;
        if (warpElapsed >= 2.0) openControlPanel();
      }

      if (Math.abs(camera.fov - targetFov) > 0.05) {
        camera.fov += (targetFov - camera.fov) * Math.min(1, dt * 4.8);
        camera.updateProjectionMatrix();
      }

      let hasRepulse = false;
      if (pointerActive.active && warpPhase === "idle") {
        raycaster.setFromCamera(pointerNDC, camera);
        if (raycaster.ray.intersectPlane(planeZ0, worldHit)) {
          particleGroup.updateMatrixWorld();
          localHit.copy(worldHit);
          particleGroup.worldToLocal(localHit);
          hasRepulse = true;
        }
      }

      const colorEase = Math.min(1, dt * 5.0);
      const posArr = mainGeo.attributes.position.array;
      const colArr = mainGeo.attributes.color.array;

      for (let i = 0; i < PARTICLE_COUNT; i++) {
        const ix = i * 3;
        let x = posArr[ix + 0];
        let y = posArr[ix + 1];
        let z = posArr[ix + 2];
        let vx = velocities[ix + 0];
        let vy = velocities[ix + 1];
        let vz = velocities[ix + 2];

        if (activeSpring > 0) {
          vx += (targetPositions[ix + 0] - x) * activeSpring * dt;
          vy += (targetPositions[ix + 1] - y) * activeSpring * dt;
          vz += (targetPositions[ix + 2] - z) * activeSpring * dt;
        }

        if (hasRepulse) {
          const rx = x - localHit.x;
          const ry = y - localHit.y;
          const rz = z - localHit.z;
          const dSq = rx * rx + ry * ry + rz * rz;
          if (dSq < 2.25 && dSq > 0.0001) {
            const d = Math.sqrt(dSq);
            const force = (1.5 - d) * 26.0 * dt;
            vx += (rx / d) * force;
            vy += (ry / d) * force;
            vz += (rz / d) * force;
          }
        }

        if (warpPhase !== "fling") {
          const damp = Math.max(0, 1 - DAMPING * dt);
          vx *= damp;
          vy *= damp;
          vz *= damp;
        }

        x += vx * dt;
        y += vy * dt;
        z += vz * dt;

        posArr[ix + 0] = x;
        posArr[ix + 1] = y;
        posArr[ix + 2] = z;
        velocities[ix + 0] = vx;
        velocities[ix + 1] = vy;
        velocities[ix + 2] = vz;

        colArr[ix + 0] += (targetColors[ix + 0] - colArr[ix + 0]) * colorEase;
        colArr[ix + 1] += (targetColors[ix + 1] - colArr[ix + 1]) * colorEase;
        colArr[ix + 2] += (targetColors[ix + 2] - colArr[ix + 2]) * colorEase;
      }

      mainGeo.attributes.position.needsUpdate = true;
      mainGeo.attributes.color.needsUpdate = true;
      renderer.render(scene, camera);
    }

    animate();
    return true;
  }

  // ---------------------------------------------------------------
  // Fallback Engine: 3D-Projected 2D Canvas (runs if WebGL or CDN unavailable)
  // ---------------------------------------------------------------
  function startFallback2DEngine() {
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let w = 800;
    let h = 640;
    let dpr = 1;
    function resize2D() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = Math.max(wrap.clientWidth || window.innerWidth, 300);
      h = Math.max(wrap.clientHeight || 640, 320);
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    window.addEventListener("resize", resize2D);
    resize2D();

    const pos = new Float32Array(PARTICLE_COUNT * 3);
    const vel = new Float32Array(PARTICLE_COUNT * 3);
    const col = new Float32Array(PARTICLE_COUNT * 3);
    const tgt = new Float32Array(PARTICLE_COUNT * 3);
    const tgtCol = new Float32Array(PARTICLE_COUNT * 3);

    function setShape2D(idx, vortex) {
      const src = shapeTargets[idx];
      for (let i = 0; i < PARTICLE_COUNT; i++) {
        const ix = i * 3;
        tgt[ix + 0] = src[ix + 0];
        tgt[ix + 1] = src[ix + 1];
        tgt[ix + 2] = src[ix + 2];
        const c = colorFromX(src[ix + 0]);
        tgtCol[ix + 0] = c[0];
        tgtCol[ix + 1] = c[1];
        tgtCol[ix + 2] = c[2];
        if (vortex) {
          vel[ix + 0] += -pos[ix + 1] * 2.5 + (Math.random() - 0.5) * 3.5;
          vel[ix + 1] += pos[ix + 0] * 2.5 + (Math.random() - 0.5) * 3.5;
          vel[ix + 2] += (Math.random() - 0.5) * 3.5;
        }
      }
      updateTaglineHighlight(idx);
    }

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const ix = i * 3;
      pos[ix + 0] = (Math.random() - 0.5) * 9;
      pos[ix + 1] = (Math.random() - 0.5) * 5;
      pos[ix + 2] = (Math.random() - 0.5) * 4;
      col[ix + 0] = HEX_CYAN[0];
      col[ix + 1] = HEX_CYAN[1];
      col[ix + 2] = HEX_CYAN[2];
    }
    setShape2D(0, false);

    const ringAngles = new Float32Array(RING_COUNT);
    for (let i = 0; i < RING_COUNT; i++) ringAngles[i] = (i / RING_COUNT) * Math.PI * 2;
    const starPts = [];
    for (let i = 0; i < STAR_COUNT; i++) {
      starPts.push([(Math.random() - 0.5) * 2, (Math.random() - 0.5) * 2, Math.random()]);
    }

    const pointer = { x: 0, y: 0, active: false };
    canvas.addEventListener("pointermove", (e) => {
      const r = canvas.getBoundingClientRect();
      pointer.x = ((e.clientX - r.left) / r.width - 0.5) * 8.0;
      pointer.y = -((e.clientY - r.top) / r.height - 0.5) * 5.0;
      pointer.active = true;
    }, { passive: true });
    canvas.addEventListener("pointerleave", () => { pointer.active = false; }, { passive: true });
    canvas.addEventListener("pointerdown", () => {
      for (let i = 0; i < PARTICLE_COUNT; i++) {
        const ix = i * 3;
        const d = Math.hypot(pos[ix], pos[ix + 1]) + 0.1;
        vel[ix] += (pos[ix] / d) * 3.2 + (Math.random() - 0.5) * 2.0;
        vel[ix + 1] += (pos[ix + 1] / d) * 3.2 + (Math.random() - 0.5) * 2.0;
      }
    }, { passive: true });

    let warpPhase = "idle";
    let warpElapsed = 0;
    warpBtn.addEventListener("click", () => {
      if (warpPhase !== "idle") return;
      warpPhase = "fling";
      warpElapsed = 0;
      warpBtn.style.opacity = "0.35";
      warpBtn.style.pointerEvents = "none";
      setShape2D(4, false);
      for (let i = 0; i < PARTICLE_COUNT; i++) {
        const ix = i * 3;
        const rad = Math.hypot(pos[ix], pos[ix + 1]) + 0.1;
        vel[ix] = (pos[ix] / rad) * (5 + Math.random() * 5);
        vel[ix + 1] = (pos[ix + 1] / rad) * (5 + Math.random() * 5);
        vel[ix + 2] = 9 + Math.random() * 11;
      }
    });

    let shapeIdx = 0;
    let shapeTimer = 0;
    let lastNow = performance.now();
    let elapsed = 0;
    let camZ = 7.4;

    function loop2D(now) {
      requestAnimationFrame(loop2D);
      const dt = Math.min((now - lastNow) / 1000, 0.05);
      lastNow = now;
      elapsed += dt;

      if (warpPhase === "idle") {
        shapeTimer += dt;
        if (shapeTimer >= SHAPE_HOLD_TIMES[shapeIdx]) {
          shapeTimer = 0;
          shapeIdx = (shapeIdx + 1) % shapeTargets.length;
          setShape2D(shapeIdx, true);
        }
      }

      let spring = 14.0;
      if (warpPhase === "fling") {
        warpElapsed += dt;
        spring = 0.0;
        camZ += (4.5 - camZ) * dt * 3;
        if (warpElapsed >= 1.4) {
          for (let i = 0; i < PARTICLE_COUNT; i++) {
            const ix = i * 3;
            pos[ix] = (Math.random() - 0.5) * 16;
            pos[ix + 1] = (Math.random() - 0.5) * 9;
            pos[ix + 2] = -30 - Math.random() * 20;
            vel[ix] *= 0.2;
            vel[ix + 1] *= 0.2;
            vel[ix + 2] = 8;
          }
          warpPhase = "reform";
          warpElapsed = 0;
        }
      } else if (warpPhase === "reform") {
        warpElapsed += dt;
        camZ += (7.4 - camZ) * dt * 4;
        spring = Math.min(18.0, 3.0 + warpElapsed * 11.0);
        if (warpElapsed >= 1.15) {
          warpPhase = "granted";
          warpElapsed = 0;
          accessMsg.classList.add("show");
        }
      } else if (warpPhase === "granted") {
        warpElapsed += dt;
        if (warpElapsed >= 2.0) openControlPanel();
      }

      ctx.globalCompositeOperation = "source-over";
      ctx.fillStyle = "#04051a";
      ctx.fillRect(0, 0, w, h);

      ctx.globalCompositeOperation = "lighter";
      const focal = Math.min(w, h) * 0.92;
      const swayY = Math.sin(elapsed * 0.42) * 0.14;
      const cosY = Math.cos(swayY);
      const sinY = Math.sin(swayY);

      // Stars
      ctx.fillStyle = "rgba(180, 230, 255, 0.45)";
      for (let i = 0; i < starPts.length; i++) {
        const s = starPts[i];
        const sx = (s[0] * 0.5 + 0.5) * w;
        const sy = (s[1] * 0.5 + 0.5) * h;
        ctx.fillRect(sx, sy, 1.5, 1.5);
      }

      // Rotating ring
      for (let i = 0; i < RING_COUNT; i++) {
        const a = ringAngles[i] + elapsed * 0.45;
        const rx = Math.cos(a) * 3.55;
        const rz = Math.sin(a) * 3.55;
        const ry = rz * 0.42;
        const depth = camZ - rz * 0.5;
        if (depth <= 0.4) continue;
        const px = w * 0.5 + (rx * focal) / depth;
        const py = h * 0.5 - (ry * focal) / depth;
        ctx.fillStyle = (i % 2 === 0) ? "rgba(0, 245, 212, 0.72)" : "rgba(241, 91, 181, 0.72)";
        ctx.fillRect(px, py, 2.2, 2.2);
      }

      // Main 5,400 particles
      const colorEase = Math.min(1, dt * 5.0);
      for (let i = 0; i < PARTICLE_COUNT; i++) {
        const ix = i * 3;
        if (spring > 0) {
          vel[ix] += (tgt[ix] - pos[ix]) * spring * dt;
          vel[ix + 1] += (tgt[ix + 1] - pos[ix + 1]) * spring * dt;
          vel[ix + 2] += (tgt[ix + 2] - pos[ix + 2]) * spring * dt;
        }
        if (pointer.active && warpPhase === "idle") {
          const rx = pos[ix] - pointer.x;
          const ry = pos[ix + 1] - pointer.y;
          const dSq = rx * rx + ry * ry;
          if (dSq < 2.25 && dSq > 0.0001) {
            const d = Math.sqrt(dSq);
            const f = (1.5 - d) * 24.0 * dt;
            vel[ix] += (rx / d) * f;
            vel[ix + 1] += (ry / d) * f;
          }
        }
        if (warpPhase !== "fling") {
          const damp = Math.max(0, 1 - 6.0 * dt);
          vel[ix] *= damp;
          vel[ix + 1] *= damp;
          vel[ix + 2] *= damp;
        }
        pos[ix] += vel[ix] * dt;
        pos[ix + 1] += vel[ix + 1] * dt;
        pos[ix + 2] += vel[ix + 2] * dt;

        col[ix] += (tgtCol[ix] - col[ix]) * colorEase;
        col[ix + 1] += (tgtCol[ix + 1] - col[ix + 1]) * colorEase;
        col[ix + 2] += (tgtCol[ix + 2] - col[ix + 2]) * colorEase;

        const rx = pos[ix] * cosY - pos[ix + 2] * sinY;
        const rz = pos[ix] * sinY + pos[ix + 2] * cosY;
        const depth = camZ - rz;
        if (depth <= 0.35) continue;

        const sx = w * 0.5 + (rx * focal) / depth;
        const sy = h * 0.5 - (pos[ix + 1] * focal) / depth;
        const r = Math.floor(col[ix] * 255);
        const g = Math.floor(col[ix + 1] * 255);
        const b = Math.floor(col[ix + 2] * 255);
        ctx.fillStyle = `rgba(${r},${g},${b},0.85)`;
        ctx.fillRect(sx - 1.1, sy - 1.1, 2.3, 2.3);
      }
    }

    requestAnimationFrame(loop2D);
  }

  // Start Three.js WebGL first; automatically fall back to 2D projected particles if blocked
  if (!startThreeEngine()) {
    startFallback2DEngine();
  }
})();
</script>
</body>
</html>
"""


def show_landing() -> None:
    """Render the interactive Three.js particle-morph landing page before the app."""
    if st.query_params.get("enter") == "1":
        st.session_state.entered = True
        st.session_state["entered_app"] = True
        st.query_params.clear()
        st.rerun()

    st.markdown(
        """
<style>
header[data-testid="stHeader"],
#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
    display: none !important;
    visibility: hidden !important;
}

.stApp {
    background: #04051a !important;
}

.block-container {
    max-width: 1120px !important;
    padding-top: 0.75rem !important;
    padding-bottom: 1.5rem !important;
}

div.stButton > button {
    width: 100%;
    padding: 0.85rem 1.8rem !important;
    border-radius: 14px !important;
    border: 1px solid #00f5d4 !important;
    background: linear-gradient(135deg, rgba(0, 245, 212, 0.16), rgba(155, 93, 229, 0.22)) !important;
    color: #00f5d4 !important;
    font-size: 1.05rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    box-shadow: 0 0 24px rgba(0, 245, 212, 0.42), inset 0 0 12px rgba(0, 245, 212, 0.18) !important;
    animation: neonPulse 2.2s ease-in-out infinite !important;
    transition: transform 0.22s ease, box-shadow 0.22s ease, background 0.22s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-2px) scale(1.015) !important;
    background: linear-gradient(135deg, rgba(0, 245, 212, 0.28), rgba(241, 91, 181, 0.25)) !important;
    color: #ffffff !important;
    box-shadow: 0 0 36px rgba(0, 245, 212, 0.78), 0 0 18px rgba(241, 91, 181, 0.45) !important;
}

@keyframes neonPulse {
    0%, 100% {
        box-shadow: 0 0 20px rgba(0, 245, 212, 0.38), inset 0 0 10px rgba(0, 245, 212, 0.15);
    }
    50% {
        box-shadow: 0 0 34px rgba(0, 245, 212, 0.75), inset 0 0 16px rgba(0, 245, 212, 0.28);
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )

    components.html(LANDING_HTML, height=640, scrolling=False)

    _, center_col, _ = st.columns([1, 1.3, 1])
    with center_col:
        if st.button("Enter Control Panel", key="enter_control_panel_btn"):
            st.session_state.entered = True
            st.session_state["entered_app"] = True
            st.rerun()
