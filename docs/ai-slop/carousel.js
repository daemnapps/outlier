/* carousel.js — the objects from the trip, riding one carousel.

   The piece ends on a tiny carousel spinning by a phone that glows Goja purple.
   This is that carousel, big enough to ride: every object is a seat, bobbing on
   its pole like a carousel horse and turning on its own axis. Drag sideways
   (thumb or mouse) and it spins with weight, then settles an object front and
   centre. Leave it alone and it turns on its own, slowly, like a music box.

   Markup:   <div class="carousel" id="carousel"></div>
             <p class="label" id="carousel-label"></p>
   Needs the three.js import map (same CDN build as /objects3d.js).

   Colours come from the system's tokens (--bone, --paper, --ink, --violet), so
   nothing here invents a colour. Loads when the section scrolls near, renders
   only while on screen, pixel ratio capped at 2.
*/
import * as THREE from 'three';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';

const SEATS = [
  ['koi', 'Koi', 'swims through the iris'],
  ['goja-sign', 'Goja sign', 'the neon that opens the loop'],
  ['chicken-heart-skewer', 'Chicken-heart skewer', 'pops in on the street-food burst'],
  ['beerlao', 'Beerlao', 'pops in on the night-out burst'],
  ['disco-ball', 'Disco ball', 'pops in on the dance-floor burst'],
  ['longtail-boat', 'Longtail boat', 'pops in on the river burst'],
  ['desk-headphones', 'Headphones', 'back at the desk'],
  ['helmet', 'Helmet', 'the motorbike selfie'],
  ['temple', 'Temple', 'circles Patuxai'],
  ['padel-racket', 'Padel racket', 'swings with every shot'],
  ['padel-ball', 'Padel ball', 'hits the lens'],
  ['sticky-rice-basket', 'Sticky-rice basket', 'crosses the footbridge'],
  ['bag-cream-strap', 'Cream-strap bag', 'runs in reverse'],
  ['bag-black-pouch', 'Black pouch', 'packed for the trip'],
  ['turntable', 'Turntable', 'rides the carousel at the end'],
  ['vinyl', 'Vinyl', 'the record the loop spins on'],
  ['gold-glasses', 'Gold glasses', 'worn on the trip'],
  ['monk', 'Monk', 'sits in the corner the whole piece'],
];

const CALM = matchMedia('(prefers-reduced-motion:reduce)').matches;
const N = SEATS.length, STEP = Math.PI * 2 / N;
const R = 2.6;                 // ring radius (seat poles)
const DECK = R + .55;          // platform radius
const TOP = 2.05;              // where the canopy starts
const SIZE = 1.0;               // an object's biggest side on its seat
const IDLE = .16;              // music-box spin, radians a second

const tok = (n, f) => (getComputedStyle(document.documentElement).getPropertyValue(n).trim() || f);

export function mountCarousel(el, label){
  const C = {bone: tok('--bone', '#EFE9E1'), paper: tok('--paper', '#F7F4EF'), ink: tok('--ink', '#171512'),
             violet: tok('--violet', '#6D3BF5')};
  const col = c => new THREE.Color(c);

  /* ── renderer, room light ─────────────────────────────────────────── */
  const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true, powerPreference:'high-performance'});
  renderer.setPixelRatio(Math.min(2, devicePixelRatio || 1));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
  renderer.setClearColor(0x000000, 0);
  const cv = renderer.domElement; cv.setAttribute('aria-hidden', 'true'); el.appendChild(cv);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), .04).texture;
  const key = new THREE.DirectionalLight(0xffffff, 1.4); key.position.set(-3, 6, 5); scene.add(key);
  const glow = new THREE.PointLight(col(C.violet), 5, 7, 1.6); glow.position.set(0, TOP - .15, 0); scene.add(glow);

  const cam = new THREE.PerspectiveCamera(32, 1, .1, 60);

  /* ── the carousel itself ──────────────────────────────────────────── */
  const ride = new THREE.Group(); scene.add(ride);          // everything that turns
  const brass = new THREE.MeshPhysicalMaterial({color:col(C.bone), metalness:1, roughness:.28, envMapIntensity:1.2});
  const mirror = new THREE.MeshPhysicalMaterial({color:col(C.paper), metalness:1, roughness:.04, envMapIntensity:1.4});
  const deckMat = new THREE.MeshPhysicalMaterial({color:col(C.bone), roughness:.45, clearcoat:.5, clearcoatRoughness:.2});
  const inkMat = new THREE.MeshPhysicalMaterial({color:col(C.ink), roughness:.5, clearcoat:.4, clearcoatRoughness:.3});

  // the deck: a bone floor on an ink plinth, brass edge
  ride.add(mesh(new THREE.CylinderGeometry(DECK, DECK, .12, 128), deckMat, 0, -.06));
  ride.add(mesh(new THREE.CylinderGeometry(DECK + .12, DECK + .2, .22, 128), inkMat, 0, -.23));
  ride.add(mesh(new THREE.TorusGeometry(DECK + .01, .025, 12, 160), brass, 0, 0, m => m.rotation.x = Math.PI / 2));

  // the centre: a mirrored column between brass collars
  ride.add(mesh(new THREE.CylinderGeometry(.42, .42, TOP, 12, 1), mirror, 0, TOP / 2));
  ride.add(mesh(new THREE.CylinderGeometry(.5, .5, .14, 48), brass, 0, .07));
  ride.add(mesh(new THREE.CylinderGeometry(.5, .5, .12, 48), brass, 0, TOP - .06));

  // the canopy: bone and ink stripes, one per seat, with a violet band at the rim
  const stripes = document.createElement('canvas'); stripes.width = N * 32; stripes.height = 256;
  const g = stripes.getContext('2d');
  for(let i = 0; i < N; i++){ g.fillStyle = i % 2 ? C.ink : C.bone; g.fillRect(i * 32, 0, 32, 256); }
  g.fillStyle = C.violet; g.fillRect(0, 232, stripes.width, 10);
  const sTex = new THREE.CanvasTexture(stripes); sTex.colorSpace = THREE.SRGBColorSpace; sTex.anisotropy = 4;
  const canopyMat = new THREE.MeshPhysicalMaterial({map:sTex, roughness:.55, sheen:.6, sheenRoughness:.6, side:THREE.DoubleSide});
  ride.add(mesh(new THREE.ConeGeometry(DECK + .2, .95, N * 4, 1, true), canopyMat, 0, TOP + .5, m => m.rotation.y = STEP / 2));
  // the valance: a short skirt of the same stripes
  const skirt = sTex.clone(); skirt.repeat.set(1, .25); skirt.offset.set(0, 0); skirt.needsUpdate = true;
  const skirtMat = canopyMat.clone(); skirtMat.map = skirt;
  ride.add(mesh(new THREE.CylinderGeometry(DECK + .2, DECK + .2, .24, N * 4, 1, true), skirtMat, 0, TOP - .1,
    m => m.rotation.y = STEP / 2));
  ride.add(mesh(new THREE.TorusGeometry(DECK + .2, .03, 12, 160), brass, 0, TOP + .02, m => m.rotation.x = Math.PI / 2));
  ride.add(mesh(new THREE.TorusGeometry(DECK + .2, .03, 12, 160), brass, 0, TOP - .22, m => m.rotation.x = Math.PI / 2));
  // the finial
  ride.add(mesh(new THREE.SphereGeometry(.13, 32, 16), brass, 0, TOP + 1.04));
  ride.add(mesh(new THREE.ConeGeometry(.04, .3, 16), brass, 0, TOP + 1.28));

  // the bulbs: Goja purple, round the canopy rim, with a soft halo each
  const bulbMat = new THREE.MeshStandardMaterial({color:col(C.violet), emissive:col(C.violet), emissiveIntensity:3.2, roughness:.3});
  const halo = document.createElement('canvas'); halo.width = halo.height = 64;
  const hg = halo.getContext('2d'), rg = hg.createRadialGradient(32, 32, 0, 32, 32, 32);
  rg.addColorStop(0, 'rgba(255,255,255,1)'); rg.addColorStop(.35, 'rgba(255,255,255,.35)'); rg.addColorStop(1, 'rgba(255,255,255,0)');
  hg.fillStyle = rg; hg.fillRect(0, 0, 64, 64);
  const hTex = new THREE.CanvasTexture(halo);
  const BULBS = N * 2, bulbs = [];
  const bulbGeo = new THREE.SphereGeometry(.045, 16, 10);
  for(let i = 0; i < BULBS; i++){
    const a = i / BULBS * Math.PI * 2, x = Math.sin(a) * (DECK + .24), z = Math.cos(a) * (DECK + .24);
    const b = mesh(bulbGeo, bulbMat, x, TOP - .23); b.position.z = z; ride.add(b);
    const s = new THREE.Sprite(new THREE.SpriteMaterial({map:hTex, color:col(C.violet), transparent:true, opacity:.55,
      depthWrite:false}));
    s.scale.setScalar(.34); s.position.set(x, TOP - .23, z); ride.add(s); bulbs.push(s);
  }
  // a second ring of bulbs up the canopy
  for(let i = 0; i < N; i++){
    const a = (i + .5) * STEP, r = (DECK + .2) * .5;
    const b = mesh(bulbGeo, bulbMat, Math.sin(a) * r, TOP + .5); b.position.z = Math.cos(a) * r; ride.add(b);
  }

  // a soft shadow on the page under the whole thing (it does not turn)
  const sh = document.createElement('canvas'); sh.width = sh.height = 128;
  const sg = sh.getContext('2d'), sgr = sg.createRadialGradient(64, 64, 20, 64, 64, 64);
  sgr.addColorStop(0, 'rgba(0,0,0,.28)'); sgr.addColorStop(1, 'rgba(0,0,0,0)'); sg.fillStyle = sgr; sg.fillRect(0, 0, 128, 128);
  const shadow = mesh(new THREE.PlaneGeometry((DECK + .6) * 2.3, (DECK + .6) * 2.3),
    new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(sh), color:col(C.ink), transparent:true, depthWrite:false}), 0, -.35,
    m => m.rotation.x = -Math.PI / 2);
  scene.add(shadow);

  // the seats: a brass pole each, the object riding on it
  const seats = SEATS.map(([id], i) => {
    const a = i * STEP, seat = new THREE.Group();
    seat.position.set(Math.sin(a) * R, 0, Math.cos(a) * R);
    seat.add(mesh(new THREE.CylinderGeometry(.028, .028, TOP - .22, 12), brass, 0, (TOP - .22) / 2));
    const rider = new THREE.Group(); seat.add(rider);
    ride.add(seat);
    return {id, seat, rider, obj:null, born:0, phase:i * STEP * 3};
  });

  /* ── load the riders, front seats first ───────────────────────────── */
  const loader = new GLTFLoader(); loader.setMeshoptDecoder(MeshoptDecoder);
  const base = new URL('objects/', import.meta.url);
  const order = seats.map((s, i) => [Math.min(i, N - i), s]).sort((a, b) => a[0] - b[0]).map(x => x[1]);
  let q = 0;
  const next = () => {
    const s = order[q++]; if(!s) return;
    loader.load(new URL(s.id + '.glb', base).href, gl => {
      const o = gl.scene, box = new THREE.Box3().setFromObject(o), size = box.getSize(new THREE.Vector3());
      o.position.sub(box.getCenter(new THREE.Vector3()));
      const holder = new THREE.Group(); holder.add(o); holder.scale.setScalar(SIZE / Math.max(size.x, size.y, size.z));
      o.traverse(m => { if(m.isMesh && m.material){ m.material.envMapIntensity = 1.1; } });
      s.rider.add(holder); s.obj = holder; s.born = performance.now(); s.rider.scale.setScalar(.001);
      next();
    }, undefined, e => { console.warn('carousel: could not load', s.id, e); next(); });
  };
  for(let i = 0; i < 4; i++) next();

  /* ── motion: drag with weight, snap to a seat, music-box idle ─────── */
  let rot = 0, vel = 0, mode = CALM ? 'rest' : 'idle', target = 0, restAt = 0, front = -1;
  let ppu = 100;                                           // screen px per world unit at the front seat
  let drag = null;

  const nearest = r => Math.round(r / STEP) * STEP;
  cv.style.touchAction = 'pan-y'; el.style.touchAction = 'pan-y';
  el.addEventListener('pointerdown', e => {
    if(e.button > 0) return;
    drag = {id:e.pointerId, x0:e.clientX, y0:e.clientY, x:e.clientX, t:performance.now(), h:null};
  });
  el.addEventListener('pointermove', e => {
    if(!drag || e.pointerId !== drag.id) return;
    const dx = e.clientX - drag.x0, dy = e.clientY - drag.y0;
    if(drag.h === null){
      if(Math.hypot(dx, dy) < 6) return;
      drag.h = Math.abs(dx) > Math.abs(dy);
      if(!drag.h){ drag = null; return; }                  // a vertical swipe is the page's, not ours
      try{ el.setPointerCapture(e.pointerId); }catch(_){}
      mode = 'drag'; vel = 0; el.classList.add('grabbing');
    }
    const now = performance.now(), d = (e.clientX - drag.x) / (R * ppu), dt = Math.max(1, now - drag.t) / 1000;
    rot += d; vel = vel * .6 + (d / dt) * .4;
    drag.x = e.clientX; drag.t = now; e.preventDefault(); wake();
  });
  const up = e => {
    if(!drag || e.pointerId !== drag.id) return;
    if(drag.h){
      if(performance.now() - drag.t > 90) vel = 0;           // held still before letting go: no fling
      vel = Math.max(-9, Math.min(9, vel)); mode = 'free'; el.classList.remove('grabbing');
    }
    drag = null; wake();
  };
  el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up);
  el.tabIndex = 0;
  el.addEventListener('keydown', e => {
    if(e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
    e.preventDefault(); target = nearest(rot) + (e.key === 'ArrowRight' ? STEP : -STEP); mode = 'snap'; wake();
  });

  function step(dt, now){
    if(mode === 'free'){
      vel *= Math.exp(-1.6 * dt); rot += vel * dt;
      if(Math.abs(vel) < .9){ target = nearest(rot + vel * .35); mode = 'snap'; }
    } else if(mode === 'snap'){
      const k = 26, c = 2 * Math.sqrt(k) * .85;
      vel += (k * (target - rot) - c * vel) * dt; rot += vel * dt;
      if(Math.abs(target - rot) < 1e-3 && Math.abs(vel) < 2e-3){ rot = target; vel = 0; mode = 'rest'; restAt = now; }
    } else if(mode === 'rest'){
      if(!CALM && now - restAt > 3200) mode = 'idle';
    } else if(mode === 'idle'){
      vel += (IDLE - vel) * Math.min(1, dt * .7); rot += vel * dt;
    }
    ride.rotation.y = rot;
    const t = now / 1000;
    for(const s of seats){
      s.rider.position.y = 1.0 + (CALM ? 0 : Math.sin(t * 1.5 + s.phase) * .13);
      s.rider.rotation.y = (CALM ? 0 : t * .35) - rot + s.phase * .2;   // turns on its own, not with the ride
      if(s.obj){ const k = Math.min(1, (now - s.born) / 600); s.rider.scale.setScalar(.001 + (1 - Math.pow(1 - k, 3)) * .999); }
    }
    // the bulbs chase round the rim, softly
    bulbs.forEach((b, i) => { b.material.opacity = CALM ? .5 : .38 + .3 * (.5 + .5 * Math.sin(t * 3 - i * .55)); });
    const f = ((Math.round(-rot / STEP) % N) + N) % N;
    if(f !== front){ front = f; const [, name, cap] = SEATS[f]; if(label) label.textContent = `${name} — ${cap}`; }
  }

  /* ── size, camera, render only while seen ─────────────────────────── */
  function fit(){
    const w = el.clientWidth, h = el.clientHeight; if(!w || !h) return;
    renderer.setSize(w, h, false);
    const aspect = w / h, narrow = aspect < 1;
    cam.fov = narrow ? 40 : 30; cam.aspect = aspect;
    const vt = Math.tan(THREE.MathUtils.degToRad(cam.fov / 2)), ht = vt * aspect;
    const W = narrow ? 3.6 : (DECK + .5) * 2, H = narrow ? 4.4 : 4.9;            // phones frame the front seats; desktop the whole ride
    const dist = Math.max(H / 2 / vt, W / 2 / ht);
    const lookY = narrow ? 1.15 : 1.2, elev = .2;
    cam.position.set(0, lookY + Math.sin(elev) * dist, Math.cos(elev) * dist);
    cam.lookAt(0, lookY, 0); cam.updateProjectionMatrix();
    ppu = h / (2 * (dist - R) * vt);
  }
  new ResizeObserver(() => { fit(); wake(); }).observe(el);
  fit();

  let seen = true, raf = 0, last = performance.now();
  function loop(now){
    raf = 0;
    const dt = Math.min(.05, (now - last) / 1000); last = now;
    step(dt, now); renderer.render(scene, cam);
    if(seen && !document.hidden) raf = requestAnimationFrame(loop);
  }
  function wake(){ if(!raf && seen){ last = performance.now(); raf = requestAnimationFrame(loop); } }
  new IntersectionObserver(es => { seen = es[0].isIntersecting; wake(); }).observe(el);
  document.addEventListener('visibilitychange', wake);
  wake();
  return {spin:v => { vel = v; mode = 'free'; wake(); }, get front(){ return SEATS[front] && SEATS[front][0]; }};
}

function mesh(geo, mat, x = 0, y = 0, f){
  const m = new THREE.Mesh(geo, mat); m.position.set(x, y, 0); if(f) f(m); return m;
}

/* start loading only when the section is near */
const el = document.getElementById('carousel');
if(el){
  let ok = false;
  try{ const p = document.createElement('canvas'); ok = !!(p.getContext('webgl2') || p.getContext('webgl')); }catch(_){}
  if(ok){
    const near = new IntersectionObserver(es => {
      if(!es.some(e => e.isIntersecting)) return;
      near.disconnect();
      window.daemnCarousel = mountCarousel(el, document.getElementById('carousel-label'));
    }, {rootMargin:'600px 0px'});
    near.observe(el);
  }
}
