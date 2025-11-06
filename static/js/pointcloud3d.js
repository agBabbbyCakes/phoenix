// 3D Point Cloud Visualization
(function() {
  'use strict';
  
  let renderer, scene, camera, stats;
  let pointclouds;
  let raycaster;
  let intersection = null;
  let spheresIndex = 0;
  let clock;
  let toggle = 0;

  const pointer = new THREE.Vector2();
  const spheres = [];

  const threshold = 0.1;
  const pointSize = 0.05;
  const width = 80;
  const length = 160;
  const rotateY = new THREE.Matrix4().makeRotationY(0.005);

  // Cyber theme colors
  const COLOR_CYAN = new THREE.Color(0x00ffcc);
  const COLOR_PINK = new THREE.Color(0xff0066);
  const COLOR_MAGENTA = new THREE.Color(0xff00ff);

  function generatePointCloudGeometry(color, width, length) {
    const geometry = new THREE.BufferGeometry();
    const numPoints = width * length;

    const positions = new Float32Array(numPoints * 3);
    const colors = new Float32Array(numPoints * 3);

    let k = 0;

    for (let i = 0; i < width; i++) {
      for (let j = 0; j < length; j++) {
        const u = i / width;
        const v = j / length;
        const x = u - 0.5;
        const y = (Math.cos(u * Math.PI * 4) + Math.sin(v * Math.PI * 8)) / 20;
        const z = v - 0.5;

        positions[3 * k] = x;
        positions[3 * k + 1] = y;
        positions[3 * k + 2] = z;

        const intensity = (y + 0.1) * 5;
        colors[3 * k] = color.r * intensity;
        colors[3 * k + 1] = color.g * intensity;
        colors[3 * k + 2] = color.b * intensity;

        k++;
      }
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.computeBoundingBox();

    return geometry;
  }

  function generatePointcloud(color, width, length) {
    const geometry = generatePointCloudGeometry(color, width, length);
    const material = new THREE.PointsMaterial({ 
      size: pointSize, 
      vertexColors: true,
      transparent: true,
      opacity: 0.9
    });

    return new THREE.Points(geometry, material);
  }

  function generateIndexedPointcloud(color, width, length) {
    const geometry = generatePointCloudGeometry(color, width, length);
    const numPoints = width * length;
    const indices = new Uint16Array(numPoints);

    let k = 0;
    for (let i = 0; i < width; i++) {
      for (let j = 0; j < length; j++) {
        indices[k] = k;
        k++;
      }
    }

    geometry.setIndex(new THREE.BufferAttribute(indices, 1));

    const material = new THREE.PointsMaterial({ 
      size: pointSize, 
      vertexColors: true,
      transparent: true,
      opacity: 0.9
    });

    return new THREE.Points(geometry, material);
  }

  function generateIndexedWithOffsetPointcloud(color, width, length) {
    const geometry = generatePointCloudGeometry(color, width, length);
    const numPoints = width * length;
    const indices = new Uint16Array(numPoints);

    let k = 0;
    for (let i = 0; i < width; i++) {
      for (let j = 0; j < length; j++) {
        indices[k] = k;
        k++;
      }
    }

    geometry.setIndex(new THREE.BufferAttribute(indices, 1));
    geometry.addGroup(0, indices.length);

    const material = new THREE.PointsMaterial({ 
      size: pointSize, 
      vertexColors: true,
      transparent: true,
      opacity: 0.9
    });

    return new THREE.Points(geometry, material);
  }

  function initPointCloud(container) {
    if (renderer) {
      // Clean up existing scene
      while(scene && scene.children.length > 0) { 
        scene.remove(scene.children[0]); 
      }
      if (renderer.domElement && renderer.domElement.parentNode) {
        renderer.domElement.parentNode.removeChild(renderer.domElement);
      }
      renderer.dispose();
    }

    const canvas = container.querySelector('#pointcloudCanvas');
    if (!canvas) {
      // Create canvas if it doesn't exist
      const newCanvas = document.createElement('canvas');
      newCanvas.id = 'pointcloudCanvas';
      newCanvas.style.width = '100%';
      newCanvas.style.height = '100%';
      container.appendChild(newCanvas);
      canvas = newCanvas;
    }

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a);

    clock = new THREE.Clock();

    camera = new THREE.PerspectiveCamera(45, canvas.clientWidth / canvas.clientHeight, 1, 10000);
    camera.position.set(10, 10, 10);
    camera.lookAt(scene.position);
    camera.updateMatrix();

    // Create point clouds with cyber theme colors
    const pcBuffer = generatePointcloud(COLOR_PINK, width, length);
    pcBuffer.scale.set(5, 10, 10);
    pcBuffer.position.set(-5, 0, 0);
    scene.add(pcBuffer);

    const pcIndexed = generateIndexedPointcloud(COLOR_CYAN, width, length);
    pcIndexed.scale.set(5, 10, 10);
    pcIndexed.position.set(0, 0, 0);
    scene.add(pcIndexed);

    const pcIndexedOffset = generateIndexedWithOffsetPointcloud(COLOR_MAGENTA, width, length);
    pcIndexedOffset.scale.set(5, 10, 10);
    pcIndexedOffset.position.set(5, 0, 0);
    scene.add(pcIndexedOffset);

    pointclouds = [pcBuffer, pcIndexed, pcIndexedOffset];

    // Create spheres for interaction markers
    const sphereGeometry = new THREE.SphereGeometry(0.1, 32, 32);
    const sphereMaterial = new THREE.MeshBasicMaterial({ color: COLOR_CYAN });

    for (let i = 0; i < 40; i++) {
      const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
      sphere.visible = false;
      scene.add(sphere);
      spheres.push(sphere);
    }

    // Create renderer
    renderer = new THREE.WebGLRenderer({ 
      canvas: canvas, 
      antialias: true, 
      alpha: true 
    });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    container.appendChild(renderer.domElement);

    // Raycaster for interaction
    raycaster = new THREE.Raycaster();
    raycaster.params.Points.threshold = threshold;

    // Stats (optional)
    if (typeof Stats !== 'undefined') {
      stats = new Stats();
      container.appendChild(stats.dom);
    }

    // Event listeners
    window.addEventListener('resize', onWindowResize);
    canvas.addEventListener('pointermove', onPointerMove);

    // Start animation
    animate();
  }

  function onPointerMove(event) {
    const rect = event.target.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  }

  function onWindowResize() {
    if (!camera || !renderer) return;
    
    const canvas = renderer.domElement;
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  }

  function animate() {
    if (!renderer || !scene || !camera) return;
    
    requestAnimationFrame(animate);

    render();
    
    if (stats) stats.update();
  }

  function render() {
    if (!camera || !renderer || !scene) return;

    camera.applyMatrix4(rotateY);
    camera.updateMatrixWorld();

    raycaster.setFromCamera(pointer, camera);

    const intersections = raycaster.intersectObjects(pointclouds, false);
    intersection = (intersections.length) > 0 ? intersections[0] : null;

    if (toggle > 0.02 && intersection !== null) {
      spheres[spheresIndex].position.copy(intersection.point);
      spheres[spheresIndex].scale.set(1, 1, 1);
      spheres[spheresIndex].visible = true;
      spheresIndex = (spheresIndex + 1) % spheres.length;
      toggle = 0;
    }

    for (let i = 0; i < spheres.length; i++) {
      const sphere = spheres[i];
      sphere.scale.multiplyScalar(0.98);
      sphere.scale.clampScalar(0.01, 1);
      if (sphere.scale.x < 0.1) {
        sphere.visible = false;
      }
    }

    toggle += clock.getDelta();

    renderer.render(scene, camera);
  }

  // Cleanup function
  function cleanup() {
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
  }

  // Global functions
  window.initPointCloud = initPointCloud;
  window.cleanupPointCloud = cleanup;

})();

