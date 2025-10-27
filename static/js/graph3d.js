// 3D Graph Visualization for Bot Network
(function() {
  'use strict';
  
  let scene, camera, renderer, controls;
  let nodes = [];
  let edges = [];
  let botNetwork = new Map();
  
  function init3DGraph(container) {
    if (renderer) {
      // Clean up existing scene
      while(scene.children.length > 0) { 
        scene.remove(scene.children[0]); 
      }
      renderer.dispose();
    }
    
    const canvas = container.querySelector('#graph3dCanvas');
    if (!canvas) return;
    
    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a);
    
    // Create camera
    camera = new THREE.PerspectiveCamera(75, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
    camera.position.set(0, 0, 50);
    
    // Create renderer
    renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);
    
    const directionalLight1 = new THREE.DirectionalLight(0x00b4ff, 1);
    directionalLight1.position.set(10, 10, 10);
    scene.add(directionalLight1);
    
    const directionalLight2 = new THREE.DirectionalLight(0xff4d94, 1);
    directionalLight2.position.set(-10, -10, -10);
    scene.add(directionalLight2);
    
    // Simple orbit controls
    controls = {
      rotationX: 0,
      rotationY: 0,
      targetRotationX: 0,
      targetRotationY: 0,
      isDragging: false,
      lastMouseX: 0,
      lastMouseY: 0
    };
    
    canvas.addEventListener('mousedown', onMouseDown);
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('mouseleave', onMouseUp);
    canvas.addEventListener('wheel', onWheel);
    
    function onMouseDown(event) {
      controls.isDragging = true;
      controls.lastMouseX = event.clientX;
      controls.lastMouseY = event.clientY;
    }
    
    function onMouseMove(event) {
      if (controls.isDragging) {
        controls.targetRotationY += (event.clientX - controls.lastMouseX) * 0.01;
        controls.targetRotationX += (event.clientY - controls.lastMouseY) * 0.01;
        controls.lastMouseX = event.clientX;
        controls.lastMouseY = event.clientY;
      }
    }
    
    function onMouseUp() {
      controls.isDragging = false;
    }
    
    function onWheel(event) {
      const delta = event.deltaY * 0.01;
      camera.position.multiplyScalar(1 + delta);
    }
    
    // Initial bot nodes
    updateBotNetwork();
  }
  
  function updateBotNetwork() {
    // Get bot data from recent events
    const events = Array.from(document.querySelectorAll('#metrics-panel table tbody tr'));
    const botMap = new Map();
    
    events.forEach((row, index) => {
      const botName = row.children[1]?.textContent || `bot-${index}`;
      const latency = parseInt(row.children[3]?.textContent || '0');
      const status = row.children[4]?.querySelector('.badge')?.textContent || 'OK';
      
      if (!botMap.has(botName)) {
        botMap.set(botName, {
          name: botName,
          latency: latency,
          status: status,
          count: 0,
          connections: []
        });
      }
      
      const bot = botMap.get(botName);
      bot.count++;
      bot.latency = latency; // Update with latest
    });
    
    // Create nodes and edges
    botNetwork = botMap;
    createGraphNodes();
  }
  
  function createGraphNodes() {
    if (!scene) return;
    
    // Clear existing nodes and edges
    nodes.forEach(node => scene.remove(node));
    edges.forEach(edge => scene.remove(edge));
    nodes = [];
    edges = [];
    
    const bots = Array.from(botNetwork.values());
    if (bots.length === 0) return;
    
    // Create nodes in a 3D grid
    const gridSize = Math.ceil(Math.sqrt(bots.length));
    const spacing = 15;
    
    bots.forEach((bot, index) => {
      const i = index % gridSize;
      const j = Math.floor(index / gridSize);
      
      const geometry = new THREE.SphereGeometry(2, 16, 16);
      let material;
      
      // Color based on status
      if (bot.status === 'Error' || bot.status.includes('Error')) {
        material = new THREE.MeshPhongMaterial({ color: 0xff3b30 });
      } else if (bot.latency > 200) {
        material = new THREE.MeshPhongMaterial({ color: 0xff9500 });
      } else {
        material = new THREE.MeshPhongMaterial({ color: 0x30d158 });
      }
      
      const sphere = new THREE.Mesh(geometry, material);
      
      const x = (i - gridSize / 2) * spacing;
      const y = (j - gridSize / 2) * spacing;
      const z = (Math.random() - 0.5) * 20;
      
      sphere.position.set(x, y, z);
      sphere.userData = { bot };
      scene.add(sphere);
      nodes.push(sphere);
      
      // Add label (simple text)
      const geometryText = new THREE.PlaneGeometry(10, 2);
      const materialText = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.8 });
      const textPlane = new THREE.Mesh(geometryText, materialText);
      textPlane.position.set(x, y - 5, z);
      textPlane.lookAt(camera.position);
      scene.add(textPlane);
    });
    
    // Create edges between nodes (connect related bots)
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        if (Math.random() < 0.3) { // 30% chance of connection
          const geometry = new THREE.BufferGeometry().setFromPoints([
            nodes[i].position,
            nodes[j].position
          ]);
          const material = new THREE.LineBasicMaterial({ color: 0x60a5fa, opacity: 0.3, transparent: true });
          const line = new THREE.Line(geometry, material);
          scene.add(line);
          edges.push(line);
        }
      }
    }
  }
  
  function animate() {
    if (!renderer || !scene || !camera) return;
    
    requestAnimationFrame(animate);
    
    // Smooth rotation
    if (controls) {
      controls.rotationY += (controls.targetRotationY - controls.rotationY) * 0.1;
      controls.rotationX += (controls.targetRotationX - controls.rotationX) * 0.1;
      
      scene.rotation.y = controls.rotationY;
      scene.rotation.x = controls.rotationX;
    }
    
    // Float animation
    nodes.forEach((node, index) => {
      node.position.y += Math.sin(Date.now() * 0.001 + index) * 0.02;
    });
    
    renderer.render(scene, camera);
  }
  
  // Start animation loop
  function startAnimation() {
    if (!renderer) return;
    animate();
  }
  
  // Global functions
  window.init3DGraph = init3DGraph;
  window.start3DAnimation = startAnimation;
  window.updateBotNetwork = updateBotNetwork;
  
})();

