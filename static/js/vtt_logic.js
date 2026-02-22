/**
 * VTT Logic for DnD El Cronista
 * Handles Fabric.js canvas, camera controls, grid system, and token management.
 */

const GRID_SIZE = 64;
let vttCanvas = null;
let vttBackgroundImage = null;
let vttTokens = new Map(); // id -> fabric.Group
let vttGridLines = [];
let vttGridVisible = true;
let isDragging = false;
let lastPosX, lastPosY;

function initVTT() {
    if (vttCanvas) return;

    // Create Canvas
    vttCanvas = new fabric.Canvas('vtt-canvas', {
        selection: false, // Disable group selection for now to simplify
        backgroundColor: '#111',
        preserveObjectStacking: true // Keep tokens above grid/bg
    });

    // Resize canvas to fit container
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // --- Camera Controls (Zoom & Pan) ---

    // Zoom with Mouse Wheel
    vttCanvas.on('mouse:wheel', function (opt) {
        var delta = opt.e.deltaY;
        var zoom = vttCanvas.getZoom();
        zoom *= 0.999 ** delta;
        if (zoom > 5) zoom = 5;
        if (zoom < 0.1) zoom = 0.1;

        vttCanvas.zoomToPoint({ x: opt.e.offsetX, y: opt.e.offsetY }, zoom);
        opt.e.preventDefault();
        opt.e.stopPropagation();

        updateGridVisibility(); // Optional: Hide grid if too zoomed out
    });

    // Pan with Right Click (or Alt + Drag)
    vttCanvas.on('mouse:down', function (opt) {
        var evt = opt.e;
        if (evt.altKey || evt.button === 2) { // Right click or Alt
            this.isDragging = true;
            this.selection = false;
            this.lastPosX = evt.clientX;
            this.lastPosY = evt.clientY;
        }
    });

    vttCanvas.on('mouse:move', function (opt) {
        if (this.isDragging) {
            var e = opt.e;
            var vpt = this.viewportTransform;
            vpt[4] += e.clientX - this.lastPosX;
            vpt[5] += e.clientY - this.lastPosY;
            this.requestRenderAll();
            this.lastPosX = e.clientX;
            this.lastPosY = e.clientY;
        }
    });

    vttCanvas.on('mouse:up', function (opt) {
        // on mouse up we want to recalculate new interaction
        // for all objects, so we call setViewportTransform
        this.setViewportTransform(this.viewportTransform);
        this.isDragging = false;
        this.selection = true;
    });

    // Context Menu disable for right click pan
    const canvasWrapper = document.getElementById('vtt-canvas').parentElement;
    canvasWrapper.addEventListener('contextmenu', (e) => e.preventDefault());

    // --- Grid System ---
    drawVTTGrid();

    console.log('🎮 VTT Logic Initialized');
}

function resizeCanvas() {
    if (!vttCanvas) return;
    const container = document.getElementById('vtt-container');
    if (container) {
        vttCanvas.setWidth(container.clientWidth);
        vttCanvas.setHeight(container.clientHeight);
        vttCanvas.renderAll();
    }
}

// --- Grid Logic ---

function drawVTTGrid() {
    if (!vttCanvas) return;

    // Clear existing grid
    vttGridLines.forEach(line => vttCanvas.remove(line));
    vttGridLines = [];

    if (!vttGridVisible) { vttCanvas.renderAll(); return; }

    // Optimization: Draw grid based on CURRENT viewport, or a large static grid?
    // For simplicity/performance, let's draw a large enough static grid (e.g. 4000x4000)
    // or use a pattern. Lines are easier to manage z-index.

    const MAP_DIMENSION = 4096; // Arbitrary large size
    const numLines = Math.ceil(MAP_DIMENSION / GRID_SIZE);

    const gridRef = new fabric.Group([], {
        selectable: false, evented: false, excludeFromExport: true
    });

    for (let i = 0; i <= numLines; i++) {
        const pos = i * GRID_SIZE;
        // Vertical
        let vLine = new fabric.Line([pos, 0, pos, MAP_DIMENSION], {
            stroke: 'rgba(255,255,255,0.15)', strokeWidth: 1,
            selectable: false, evented: false
        });
        // Horizontal
        let hLine = new fabric.Line([0, pos, MAP_DIMENSION, pos], {
            stroke: 'rgba(255,255,255,0.15)', strokeWidth: 1,
            selectable: false, evented: false
        });
        gridRef.addWithUpdate(vLine);
        gridRef.addWithUpdate(hLine);
    }

    vttCanvas.add(gridRef);
    gridRef.sendToBack();
    if (vttBackgroundImage) vttBackgroundImage.sendToBack(); // Bg behind grid

    vttGridLines.push(gridRef); // Store group reference
}

function toggleGrid() {
    vttGridVisible = !vttGridVisible;
    drawVTTGrid();
}

// --- Background Logic ---

function setVTTBackground(imageUrl) {
    if (!vttCanvas) initVTT();
    if (!imageUrl) return;

    fabric.Image.fromURL(imageUrl, function (img) {
        // Ensure image fits nicely or maintains aspect ratio?
        // Let's reset zoom to show full map initially

        img.set({ originX: 'left', originY: 'top', selectable: false, evented: false });

        if (vttBackgroundImage) vttCanvas.remove(vttBackgroundImage);
        vttBackgroundImage = img;
        vttCanvas.add(img);
        img.sendToBack();

        // Ensure grid is above bg
        drawVTTGrid();

        vttCanvas.renderAll();
    }, { crossOrigin: 'anonymous' });
}

// --- Token Logic ---

function createVTTToken(config) {
    if (!vttCanvas) initVTT();
    // Default values
    const { id, name, x = 0, y = 0, color = '#00ff00', img = null, type = 'pj' } = config;

    // Smart Update: If token exists, just animate to new position
    if (vttTokens.has(id)) {
        updateVTTTokenPosition(id, x, y);
        return;
    }

    // Helper to finalize token creation
    const assembleToken = (visualObj) => {
        const label = new fabric.Text(name.length > 10 ? name.substring(0, 9) + '…' : name, {
            fontSize: 12, fill: '#ffffff',
            originX: 'center', originY: 'top',
            top: 30,
            fontFamily: 'Segoe UI, sans-serif',
            shadow: new fabric.Shadow({ color: 'rgba(0,0,0,0.8)', blur: 2, offsetX: 1, offsetY: 1 })
        });

        const group = new fabric.Group([visualObj, label], {
            left: x, top: y,
            hasControls: false,
            hasBorders: true,
            borderColor: '#2ecc71',
            padding: 2,
            lockScalingX: true, lockScalingY: true, lockRotation: true,
            originX: 'center', originY: 'center',
            subTargetCheck: true
        });

        group.tokenId = id;
        group.tokenType = type;

        // Snapping Logic
        group.on('moving', function (options) {
            // Visualize snapping? 
            // For now, just snap on release or during move? Request says "alinearse automáticamente... al terminar un movimiento"
            // But let's do it during move for better UI feel, or on modified.
            // "al terminar un movimiento (object:modified)" -> Snap on drop.
        });

        group.on('modified', function () {
            // Snap to Grid
            const snapX = Math.round(this.left / GRID_SIZE) * GRID_SIZE + (GRID_SIZE / 2);
            const snapY = Math.round(this.top / GRID_SIZE) * GRID_SIZE + (GRID_SIZE / 2);

            this.set({ left: snapX, top: snapY });
            this.setCoords();

            // Send Update
            if (window.ws && window.ws.readyState === WebSocket.OPEN) {
                window.ws.send(JSON.stringify({
                    type: 'token_moved',
                    token_id: id,
                    x: this.left, // Send snapped coords
                    y: this.top
                }));
            }
        });

        vttCanvas.add(group);
        vttTokens.set(id, group);
        vttCanvas.renderAll();
    };

    if (img) {
        // Load Avatar
        fabric.Image.fromURL(img, function (oImg) {
            if (!oImg) {
                fallbackConfig(color, type, assembleToken);
                return;
            }

            // Circular Clip
            const size = 56; // Grid is 64, leave margin
            const scale = size / Math.min(oImg.width, oImg.height);

            oImg.scale(scale);
            oImg.set({
                originX: 'center', originY: 'center',
                clipPath: new fabric.Circle({
                    radius: size / 2 / scale, // Inverse scale for clip
                    originX: 'center', originY: 'center'
                })
            });

            // Border Ring
            const ring = new fabric.Circle({
                radius: 28, // 56/2
                fill: 'transparent',
                stroke: type === 'pj' ? '#d4af37' : '#e74c3c',
                strokeWidth: 3,
                originX: 'center', originY: 'center'
            });

            const visualGroup = new fabric.Group([oImg, ring], {
                originX: 'center', originY: 'center'
            });

            assembleToken(visualGroup);

        }, { crossOrigin: 'anonymous' });
    } else {
        fallbackConfig(color, type, assembleToken);
    }
}

function fallbackConfig(color, type, callback) {
    const circle = new fabric.Circle({
        radius: 28,
        fill: color,
        stroke: type === 'pj' ? '#ffffff' : '#000000',
        strokeWidth: 3,
        originX: 'center', originY: 'center'
    });
    callback(circle);
}

function updateVTTTokenPosition(id, x, y) {
    const token = vttTokens.get(id);
    if (token) {
        token.animate({ left: x, top: y }, {
            duration: 200,
            onChange: vttCanvas.renderAll.bind(vttCanvas),
            easing: fabric.util.ease.easeOutQuad
        });
    }
}

function clearVTTTokens() {
    vttTokens.forEach(t => vttCanvas.remove(t));
    vttTokens.clear();
    vttCanvas.renderAll();
}

function showVTT() {
    const overlay = document.getElementById('vtt-overlay');
    // In new layout, VTT is likely always "there" but maybe hidden or z-index managed?
    // Maintaining compatibility with previous logic for now
    if (overlay) overlay.style.display = 'block';
    setTimeout(resizeCanvas, 100);
}

// Export functions for global use if needed (legacy inline scripts)
window.initVTT = initVTT;
window.createVTTToken = createVTTToken;
window.setVTTBackground = setVTTBackground;
window.updateVTTTokenPosition = updateVTTTokenPosition;
window.clearVTTTokens = clearVTTTokens;
window.toggleGrid = toggleGrid;
window.showVTT = showVTT;
