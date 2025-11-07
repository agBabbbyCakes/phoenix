// 3D Financial Positions Chart - Fidelity Style
// Enhanced with bookmarks, markers, tooltips, and expert data visualization features
(function() {
  'use strict';
  
  let scene, camera, renderer, controls;
  let chartData = [];
  let meshes = [];
  let markers = []; // Bookmarked data points
  let bookmarks = []; // Saved bookmarks
  let raycaster, mouse;
  let hoveredMesh = null;
  let tooltip = null;
  let gridHelper, axesHelper;
  let bookmarkPanel = null;
  
  // Dark sassy color palette (Fidelity-inspired)
  const COLORS = {
    background: 0x0a0a0f,      // Very dark blue-black
    grid: 0x1a1a2e,            // Dark blue-gray
    axis: 0x2d3561,            // Muted blue
    profit: 0x00ff88,          // Bright green (profits)
    loss: 0xff3b5c,            // Bright red (losses)
    neutral: 0x4a90e2,         // Blue (neutral)
    warning: 0xffa500,         // Orange (warnings)
    accent1: 0x9b59b6,         // Purple accent
    accent2: 0xe74c3c,         // Red accent
    text: 0xffffff,            // White text
    glow: 0x00bfff,            // Cyan glow
    bookmark: 0xffd700         // Gold for bookmarks
  };
  
  // Load bookmarks from localStorage
  function loadBookmarks() {
    try {
      const saved = localStorage.getItem('phoenix:bookmarks');
      if (saved) {
        bookmarks = JSON.parse(saved);
        updateBookmarkPanel();
      }
    } catch (e) {
      console.warn('Failed to load bookmarks', e);
    }
  }
  
  // Save bookmarks to localStorage
  function saveBookmarks() {
    try {
      localStorage.setItem('phoenix:bookmarks', JSON.stringify(bookmarks));
    } catch (e) {
      console.warn('Failed to save bookmarks', e);
    }
  }
  
  // Create bookmark panel UI
  function createBookmarkPanel(container) {
    const panel = document.createElement('div');
    panel.id = 'bookmark-panel';
    panel.style.cssText = `
      position: absolute;
      top: 10px;
      right: 10px;
      background: rgba(10, 10, 15, 0.95);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 16px;
      min-width: 280px;
      max-width: 400px;
      max-height: 60vh;
      overflow-y: auto;
      z-index: 1000;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8);
      color: #f0f0f0;
      font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
      font-size: 13px;
    `;
    
    panel.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: #00bfff;">📌 Bookmarks</h3>
        <button id="close-bookmarks" style="
          background: transparent;
          border: none;
          color: #888;
          cursor: pointer;
          font-size: 20px;
          padding: 0;
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
        ">×</button>
      </div>
      <div id="bookmark-list" style="margin-bottom: 12px;"></div>
      <div style="display: flex; gap: 8px;">
        <button id="export-bookmarks" style="
          flex: 1;
          padding: 8px 12px;
          background: rgba(0, 191, 255, 0.2);
          border: 1px solid rgba(0, 191, 255, 0.5);
          border-radius: 6px;
          color: #00bfff;
          cursor: pointer;
          font-size: 12px;
          font-weight: 500;
        ">Export</button>
        <button id="clear-bookmarks" style="
          flex: 1;
          padding: 8px 12px;
          background: rgba(255, 59, 92, 0.2);
          border: 1px solid rgba(255, 59, 92, 0.5);
          border-radius: 6px;
          color: #ff3b5c;
          cursor: pointer;
          font-size: 12px;
          font-weight: 500;
        ">Clear All</button>
      </div>
    `;
    
    container.appendChild(panel);
    bookmarkPanel = panel;
    
    // Event listeners
    document.getElementById('close-bookmarks').addEventListener('click', () => {
      panel.style.display = 'none';
    });
    
    document.getElementById('export-bookmarks').addEventListener('click', exportBookmarks);
    document.getElementById('clear-bookmarks').addEventListener('click', clearAllBookmarks);
    
    updateBookmarkPanel();
    return panel;
  }
  
  // Update bookmark panel with current bookmarks
  function updateBookmarkPanel() {
    if (!bookmarkPanel) return;
    
    const list = document.getElementById('bookmark-list');
    if (!list) return;
    
    if (bookmarks.length === 0) {
      list.innerHTML = '<div style="text-align: center; color: #888; padding: 20px;">No bookmarks yet. Right-click a data point to bookmark it.</div>';
      return;
    }
    
    list.innerHTML = bookmarks.map((bm, idx) => {
      const date = new Date(bm.timestamp).toLocaleString();
      return `
        <div style="
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          padding: 12px;
          margin-bottom: 8px;
          cursor: pointer;
          transition: all 0.2s;
        " onmouseover="this.style.background='rgba(0, 191, 255, 0.1)'" 
           onmouseout="this.style.background='rgba(255, 255, 255, 0.05)'"
           onclick="window.financial3dJumpToBookmark(${idx})">
          <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 4px;">
            <strong style="color: #00bfff;">${bm.label || 'Bookmark ' + (idx + 1)}</strong>
            <button onclick="event.stopPropagation(); window.financial3dDeleteBookmark(${idx})" style="
              background: transparent;
              border: none;
              color: #ff3b5c;
              cursor: pointer;
              font-size: 14px;
              padding: 0 4px;
            ">×</button>
          </div>
          <div style="font-size: 11px; color: #888;">
            ${date}<br>
            ${bm.bot_name || 'Unknown'} | Latency: ${bm.latency_ms || 'N/A'}ms
            ${bm.profit !== undefined ? ` | Profit: ${bm.profit >= 0 ? '+' : ''}${bm.profit.toFixed(4)}` : ''}
          </div>
        </div>
      `;
    }).join('');
  }
  
  // Export bookmarks as JSON
  function exportBookmarks() {
    const dataStr = JSON.stringify(bookmarks, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `phoenix-bookmarks-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }
  
  // Clear all bookmarks
  function clearAllBookmarks() {
    if (confirm('Clear all bookmarks?')) {
      bookmarks = [];
      markers.forEach(m => scene.remove(m));
      markers = [];
      saveBookmarks();
      updateBookmarkPanel();
    }
  }
  
  // Add bookmark
  function addBookmark(item, index, position) {
    const bookmark = {
      id: Date.now(),
      timestamp: item.timestamp || new Date().toISOString(),
      bot_name: item.bot_name,
      latency_ms: item.latency_ms || item.latency,
      profit: item.profit,
      status: item.status,
      label: `Bookmark ${bookmarks.length + 1}`,
      index: index,
      position: { x: position.x, y: position.y, z: position.z }
    };
    
    bookmarks.push(bookmark);
    saveBookmarks();
    updateBookmarkPanel();
    
    // Add visual marker
    addBookmarkMarker(position, bookmark.id);
  }
  
  // Add visual bookmark marker
  function addBookmarkMarker(position, bookmarkId) {
    const markerGeometry = new THREE.ConeGeometry(0.8, 2, 8);
    const markerMaterial = new THREE.MeshPhongMaterial({ 
      color: COLORS.bookmark,
      emissive: COLORS.bookmark,
      emissiveIntensity: 0.5
    });
    const marker = new THREE.Mesh(markerGeometry, markerMaterial);
    marker.position.set(position.x, position.y + 1, position.z);
    marker.rotation.z = Math.PI;
    marker.userData = { bookmarkId, isBookmark: true };
    
    // Add glow ring
    const ringGeometry = new THREE.RingGeometry(0.5, 1, 16);
    const ringMaterial = new THREE.MeshBasicMaterial({ 
      color: COLORS.bookmark,
      transparent: true,
      opacity: 0.6,
      side: THREE.DoubleSide
    });
    const ring = new THREE.Mesh(ringGeometry, ringMaterial);
    ring.position.set(position.x, position.y + 0.5, position.z);
    ring.rotation.x = -Math.PI / 2;
    ring.userData = { bookmarkId, isBookmark: true };
    
    scene.add(marker);
    scene.add(ring);
    markers.push(marker, ring);
  }
  
  // Create tooltip
  function createTooltip() {
    if (tooltip) return tooltip;
    
    tooltip = document.createElement('div');
    tooltip.id = 'financial3d-tooltip';
    tooltip.style.cssText = `
      position: absolute;
      background: rgba(10, 10, 15, 0.95);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(0, 191, 255, 0.5);
      border-radius: 8px;
      padding: 12px;
      pointer-events: none;
      z-index: 10000;
      color: #f0f0f0;
      font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
      font-size: 12px;
      line-height: 1.6;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.8);
      display: none;
      max-width: 300px;
    `;
    document.body.appendChild(tooltip);
    return tooltip;
  }
  
  // Show tooltip
  function showTooltip(item, x, y) {
    if (!tooltip) createTooltip();
    
    const date = item.timestamp ? new Date(item.timestamp).toLocaleString() : 'Unknown';
    const profit = item.profit !== undefined ? 
      `<span style="color: ${item.profit >= 0 ? '#00ff88' : '#ff3b5c'}">${item.profit >= 0 ? '+' : ''}${item.profit.toFixed(4)}</span>` : 
      'N/A';
    
    tooltip.innerHTML = `
      <div style="font-weight: 600; color: #00bfff; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">
        ${item.bot_name || 'Unknown Bot'}
      </div>
      <div style="margin-bottom: 4px;"><strong>Time:</strong> ${date}</div>
      <div style="margin-bottom: 4px;"><strong>Latency:</strong> ${item.latency_ms || item.latency || 'N/A'}ms</div>
      ${item.profit !== undefined ? `<div style="margin-bottom: 4px;"><strong>Profit:</strong> ${profit}</div>` : ''}
      ${item.success_ratio !== undefined ? `<div style="margin-bottom: 4px;"><strong>Success:</strong> ${item.success_ratio.toFixed(1)}%</div>` : ''}
      ${item.status ? `<div style="margin-bottom: 4px;"><strong>Status:</strong> <span style="color: ${item.status === 'ok' ? '#00ff88' : item.status === 'warning' ? '#ffa500' : '#ff3b5c'}">${item.status}</span></div>` : ''}
      ${item.tx_hash ? `<div style="margin-bottom: 4px;"><strong>TX:</strong> <code style="font-size: 10px;">${item.tx_hash}</code></div>` : ''}
      <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); font-size: 10px; color: #888;">
        Right-click to bookmark • Scroll to zoom
      </div>
    `;
    
    tooltip.style.display = 'block';
    tooltip.style.left = (x + 10) + 'px';
    tooltip.style.top = (y + 10) + 'px';
  }
  
  // Hide tooltip
  function hideTooltip() {
    if (tooltip) {
      tooltip.style.display = 'none';
    }
  }
  
  function initFinancial3D(container) {
    if (renderer) {
      cleanup();
    }
    
    const canvas = container.querySelector('#financial3dCanvas');
    if (!canvas) {
      console.error('Financial3D: Canvas not found');
      return;
    }
    
    // Scene setup
    scene = new THREE.Scene();
    scene.background = new THREE.Color(COLORS.background);
    scene.fog = new THREE.FogExp2(COLORS.background, 0.002);
    
    // Camera setup
    const aspect = canvas.clientWidth / canvas.clientHeight;
    camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 1000);
    camera.position.set(30, 40, 50);
    camera.lookAt(0, 0, 0);
    
    // Renderer setup
    renderer = new THREE.WebGLRenderer({ 
      canvas: canvas, 
      antialias: true, 
      alpha: false,
      powerPreference: "high-performance"
    });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    
    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambientLight);
    
    const directionalLight1 = new THREE.DirectionalLight(COLORS.glow, 0.8);
    directionalLight1.position.set(20, 30, 20);
    directionalLight1.castShadow = true;
    directionalLight1.shadow.mapSize.width = 2048;
    directionalLight1.shadow.mapSize.height = 2048;
    scene.add(directionalLight1);
    
    const directionalLight2 = new THREE.DirectionalLight(COLORS.accent1, 0.3);
    directionalLight2.position.set(-20, 20, -20);
    scene.add(directionalLight2);
    
    // Grid helper
    gridHelper = new THREE.GridHelper(100, 20, COLORS.grid, COLORS.grid);
    gridHelper.position.y = -5;
    scene.add(gridHelper);
    
    // Axes helper
    axesHelper = new THREE.AxesHelper(20);
    scene.add(axesHelper);
    
    // Raycaster for mouse interaction
    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();
    
    // Orbit controls (if available, otherwise use simple mouse controls)
    if (typeof THREE.OrbitControls !== 'undefined') {
      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.minDistance = 20;
      controls.maxDistance = 200;
      controls.maxPolarAngle = Math.PI / 2.2;
    } else {
      setupSimpleControls(canvas);
    }
    
    // Create bookmark panel
    createBookmarkPanel(container);
    loadBookmarks();
    
    // Mouse events for tooltips and bookmarks
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('click', onMouseClick);
    canvas.addEventListener('contextmenu', onRightClick);
    canvas.addEventListener('mouseleave', () => {
      hideTooltip();
      hoveredMesh = null;
    });
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    
    // Start animation
    animate();
  }
  
  function onMouseMove(event) {
    if (!raycaster || !camera) return;
    
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    
    raycaster.setFromCamera(mouse, camera);
    
    const intersects = raycaster.intersectObjects(meshes.filter(m => m.userData && m.userData.item));
    
    if (intersects.length > 0) {
      const intersect = intersects[0];
      if (hoveredMesh !== intersect.object) {
        hoveredMesh = intersect.object;
        if (hoveredMesh.userData && hoveredMesh.userData.item) {
          showTooltip(hoveredMesh.userData.item, event.clientX, event.clientY);
        }
      }
    } else {
      if (hoveredMesh) {
        hoveredMesh = null;
        hideTooltip();
      }
    }
  }
  
  function onMouseClick(event) {
    if (!raycaster || !camera) return;
    
    const intersects = raycaster.intersectObjects(meshes.filter(m => m.userData && m.userData.item));
    if (intersects.length > 0) {
      const intersect = intersects[0];
      const mesh = intersect.object;
      if (mesh.userData && mesh.userData.item) {
        // Highlight on click
        mesh.material.emissiveIntensity = 0.8;
        setTimeout(() => {
          if (mesh.material) mesh.material.emissiveIntensity = 0.3;
        }, 300);
      }
    }
  }
  
  function onRightClick(event) {
    event.preventDefault();
    if (!raycaster || !camera) return;
    
    const intersects = raycaster.intersectObjects(meshes.filter(m => m.userData && m.userData.item));
    if (intersects.length > 0) {
      const intersect = intersects[0];
      const mesh = intersect.object;
      if (mesh.userData && mesh.userData.item) {
        const item = mesh.userData.item;
        const index = mesh.userData.index;
        const position = mesh.position.clone();
        position.y += (mesh.geometry.parameters.height || 1) / 2;
        
        // Prompt for bookmark label
        const label = prompt('Bookmark label (optional):', `Bookmark ${bookmarks.length + 1}`);
        if (label !== null) {
          const bookmark = {
            id: Date.now(),
            timestamp: item.timestamp || new Date().toISOString(),
            bot_name: item.bot_name,
            latency_ms: item.latency_ms || item.latency,
            profit: item.profit,
            status: item.status,
            label: label || `Bookmark ${bookmarks.length + 1}`,
            index: index,
            position: { x: position.x, y: position.y, z: position.z }
          };
          
          bookmarks.push(bookmark);
          saveBookmarks();
          updateBookmarkPanel();
          addBookmarkMarker(position, bookmark.id);
        }
      }
    }
  }
  
  function setupSimpleControls(canvas) {
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    
    canvas.addEventListener('mousedown', (e) => {
      if (e.button === 0) { // Left mouse only
        isDragging = true;
        previousMousePosition = { x: e.clientX, y: e.clientY };
      }
    });
    
    canvas.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      
      const deltaX = e.clientX - previousMousePosition.x;
      const deltaY = e.clientY - previousMousePosition.y;
      
      const spherical = new THREE.Spherical();
      spherical.setFromVector3(camera.position);
      spherical.theta -= deltaX * 0.01;
      spherical.phi += deltaY * 0.01;
      spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));
      
      camera.position.setFromSpherical(spherical);
      camera.lookAt(0, 0, 0);
      
      previousMousePosition = { x: e.clientX, y: e.clientY };
    });
    
    canvas.addEventListener('mouseup', () => {
      isDragging = false;
    });
    
    canvas.addEventListener('wheel', (e) => {
      const delta = e.deltaY * 0.01;
      camera.position.multiplyScalar(1 + delta);
    });
  }
  
  function onWindowResize() {
    if (!camera || !renderer) return;
    
    const canvas = renderer.domElement;
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  }
  
  function updateData(jsonData) {
    if (!scene) return;
    
    // Clear existing meshes (but keep bookmarks)
    meshes.forEach(mesh => {
      if (!mesh.userData || !mesh.userData.isBookmark) {
        scene.remove(mesh);
      }
    });
    meshes = meshes.filter(m => m.userData && m.userData.isBookmark);
    
    // Parse data - handle both array and object formats
    let data = [];
    if (Array.isArray(jsonData)) {
      data = jsonData;
    } else if (jsonData.bots && Array.isArray(jsonData.bots)) {
      data = jsonData.bots;
    } else if (jsonData.events && Array.isArray(jsonData.events)) {
      data = jsonData.events;
    } else {
      console.warn('Financial3D: Unknown data format', jsonData);
      return;
    }
    
    if (data.length === 0) return;
    
    chartData = data;
    
    // Create 3D bars/candles for each data point
    const spacing = 3;
    const barWidth = 2;
    const maxValue = Math.max(...data.map(d => 
      d.latency_ms || d.latency || Math.abs(d.profit) || d.success_ratio || 100
    ));
    
    data.forEach((item, index) => {
      const x = (index - data.length / 2) * spacing;
      const value = item.latency_ms || item.latency || Math.abs(item.profit) || item.success_ratio || 0;
      const height = Math.max(0.5, (value / maxValue) * 30);
      
      // Determine color based on status/profit
      let color = COLORS.neutral;
      if (item.profit !== undefined) {
        color = item.profit >= 0 ? COLORS.profit : COLORS.loss;
      } else if (item.status) {
        if (item.status === 'error' || item.status === 'critical') {
          color = COLORS.loss;
        } else if (item.status === 'warning') {
          color = COLORS.warning;
        } else {
          color = COLORS.profit;
        }
      } else if (item.error) {
        color = COLORS.loss;
      }
      
      // Create bar geometry
      const geometry = new THREE.BoxGeometry(barWidth, height, barWidth);
      const material = new THREE.MeshPhongMaterial({ 
        color: color,
        emissive: color,
        emissiveIntensity: 0.3,
        shininess: 100
      });
      
      const bar = new THREE.Mesh(geometry, material);
      bar.position.set(x, height / 2, 0);
      bar.castShadow = true;
      bar.receiveShadow = true;
      bar.userData = { item, index };
      
      scene.add(bar);
      meshes.push(bar);
      
      // Add glow effect for important points
      if ((item.profit && Math.abs(item.profit) > 0.01) || (item.latency_ms && item.latency_ms > 200)) {
        const glowGeometry = new THREE.SphereGeometry(0.5, 16, 16);
        const glowMaterial = new THREE.MeshBasicMaterial({ 
          color: COLORS.glow,
          transparent: true,
          opacity: 0.6
        });
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        glow.position.set(x, height + 1, 0);
        glow.userData = { item, index };
        scene.add(glow);
        meshes.push(glow);
      }
    });
    
    // Restore bookmark markers
    bookmarks.forEach(bm => {
      if (bm.position) {
        addBookmarkMarker(new THREE.Vector3(bm.position.x, bm.position.y, bm.position.z), bm.id);
      }
    });
    
    // Add connecting lines (like a financial chart)
    if (data.length > 1) {
      const lineGeometry = new THREE.BufferGeometry();
      const positions = new Float32Array(data.length * 3);
      
      data.forEach((item, index) => {
        const x = (index - data.length / 2) * spacing;
        const value = item.latency_ms || item.latency || Math.abs(item.profit) || item.success_ratio || 0;
        const y = Math.max(0.5, (value / maxValue) * 30);
        
        positions[index * 3] = x;
        positions[index * 3 + 1] = y;
        positions[index * 3 + 2] = 0;
      });
      
      lineGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      
      const lineMaterial = new THREE.LineBasicMaterial({ 
        color: COLORS.accent1,
        linewidth: 2,
        transparent: true,
        opacity: 0.6
      });
      
      const line = new THREE.Line(lineGeometry, lineMaterial);
      scene.add(line);
      meshes.push(line);
    }
  }
  
  function animate() {
    if (!renderer || !scene || !camera) return;
    
    requestAnimationFrame(animate);
    
    // Update controls
    if (controls && controls.update) {
      controls.update();
    }
    
    // Animate bookmark markers (pulse effect)
    markers.forEach((marker, idx) => {
      if (marker.userData && marker.userData.isBookmark) {
        const time = Date.now() * 0.001;
        marker.rotation.y = time + idx;
        if (marker.material && marker.material.emissiveIntensity !== undefined) {
          marker.material.emissiveIntensity = 0.5 + Math.sin(time * 2 + idx) * 0.2;
        }
      }
    });
    
    // Subtle rotation animation for bars
    if (meshes.length > 0) {
      meshes.forEach((mesh, index) => {
        if (mesh.userData && mesh.userData.item && !mesh.userData.isBookmark) {
          mesh.rotation.y += 0.001;
        }
      });
    }
    
    renderer.render(scene, camera);
  }
  
  function cleanup() {
    if (meshes.length > 0) {
      meshes.forEach(mesh => {
        if (mesh.geometry) mesh.geometry.dispose();
        if (mesh.material) {
          if (Array.isArray(mesh.material)) {
            mesh.material.forEach(mat => mat.dispose());
          } else {
            mesh.material.dispose();
          }
        }
        if (scene) scene.remove(mesh);
      });
      meshes = [];
    }
    
    if (markers.length > 0) {
      markers.forEach(marker => {
        if (marker.geometry) marker.geometry.dispose();
        if (marker.material) marker.material.dispose();
        if (scene) scene.remove(marker);
      });
      markers = [];
    }
    
    if (tooltip && tooltip.parentNode) {
      tooltip.parentNode.removeChild(tooltip);
      tooltip = null;
    }
    
    if (bookmarkPanel && bookmarkPanel.parentNode) {
      bookmarkPanel.parentNode.removeChild(bookmarkPanel);
      bookmarkPanel = null;
    }
    
    if (renderer) {
      renderer.dispose();
      if (renderer.domElement && renderer.domElement.parentNode) {
        renderer.domElement.parentNode.removeChild(renderer.domElement);
      }
    }
    
    if (window) {
      window.removeEventListener('resize', onWindowResize);
    }
    
    scene = null;
    camera = null;
    renderer = null;
    controls = null;
  }
  
  // Jump to bookmark
  function jumpToBookmark(index) {
    if (index < 0 || index >= bookmarks.length) return;
    const bm = bookmarks[index];
    if (bm.position && camera) {
      // Animate camera to bookmark position
      const target = new THREE.Vector3(bm.position.x, bm.position.y + 10, bm.position.z + 20);
      // Simple animation (could be improved with tweening)
      camera.position.lerp(target, 0.1);
      camera.lookAt(bm.position.x, bm.position.y, bm.position.z);
    }
  }
  
  // Delete bookmark
  function deleteBookmark(index) {
    if (index < 0 || index >= bookmarks.length) return;
    const bm = bookmarks[index];
    
    // Remove visual markers
    markers = markers.filter(m => {
      if (m.userData && m.userData.bookmarkId === bm.id) {
        scene.remove(m);
        if (m.geometry) m.geometry.dispose();
        if (m.material) m.material.dispose();
        return false;
      }
      return true;
    });
    
    bookmarks.splice(index, 1);
    saveBookmarks();
    updateBookmarkPanel();
  }
  
  // Fetch data from API
  async function fetchAndUpdate(apiEndpoint = '/api/charts/data') {
    try {
      const response = await fetch(apiEndpoint);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      updateData(data);
    } catch (error) {
      console.error('Financial3D: Failed to fetch data', error);
    }
  }
  
  // Global functions
  window.initFinancial3D = initFinancial3D;
  window.updateFinancial3DData = updateData;
  window.fetchFinancial3DData = fetchAndUpdate;
  window.cleanupFinancial3D = cleanup;
  window.financial3dJumpToBookmark = jumpToBookmark;
  window.financial3dDeleteBookmark = deleteBookmark;
  
})();
