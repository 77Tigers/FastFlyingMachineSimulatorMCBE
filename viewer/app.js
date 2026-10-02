import * as THREE from 'three';

let wasm;
const utf8 = new TextDecoder();
async function loadWasm() {
  const response = await fetch('./fastflyer.wasm?v=__WASM_HASH__');
  if (!response.ok) throw Error(`Could not load simulation engine (${response.status})`);
  const {instance} = await WebAssembly.instantiate(await response.arrayBuffer(), {});
  wasm = instance.exports;
}
function runEngine(input,tick=0,simulate=false,detailed=false) {
  const bytes = input instanceof Uint8Array ? input : new Uint8Array(input);
  const pointer = wasm.ff_alloc(bytes.length);
  new Uint8Array(wasm.memory.buffer,pointer,bytes.length).set(bytes);
  const ok = wasm.ff_run(pointer,bytes.length,tick,Number(simulate),Number(detailed));
  wasm.ff_free(pointer,bytes.length);
  const copy = (ptr,len) => new Uint8Array(wasm.memory.buffer,ptr,len).slice();
  if (!ok) throw Error(utf8.decode(copy(wasm.ff_error_ptr(),wasm.ff_error_len())));
  const traceLength=wasm.ff_trace_len();
  return {bytes:copy(wasm.ff_flyer_ptr(),wasm.ff_flyer_len()),
    trace:traceLength?JSON.parse(utf8.decode(copy(wasm.ff_trace_ptr(),traceLength))):null,
    shift:[Number(wasm.ff_shift_x()),Number(wasm.ff_shift_y()),Number(wasm.ff_shift_z())]};
}
function shiftTrace(data,origin) {
  const move=pos=>{if(pos)for(let i=0;i<3;i++)pos[i]+=origin[i];};
  const movePairs=pairs=>pairs?.forEach(([a])=>move(a));
  const moveOwners=owners=>owners?.forEach(([a,b])=>{move(a);move(b);});
  const moveLinks=links=>links?.forEach(([a,b])=>{move(a);move(b);});
  const moveChunks=chunks=>chunks?.forEach(chunk=>{chunk[0]+=origin[0]/16;chunk[1]+=origin[2]/16;});
  data.initial.forEach(move);moveOwners(data.initial_owners);movePairs(data.initial_arms);
  for(const step of data.steps){
    step.changes.forEach(move);moveOwners(step.owners);movePairs(step.arms);
    moveChunks(step.chunk_order);moveChunks(step.active_chunk?[step.active_chunk]:[]);
    step.piston_order.forEach(move);move(step.active_piston);
    if(step.power){step.power.powered.forEach(move);step.power.hard.forEach(move);moveLinks(step.power.links);}
    if(step.movement){step.movement.sources.forEach(move);step.movement.destinations.forEach(move);moveLinks(step.movement.links);moveLinks(step.movement.ignored);move(step.movement.failure?.pos);}
  }
  return data;
}

const names = {1:'Slime',2:'Honey',3:'Smooth stone',4:'Glass',5:'Glazed terracotta',6:'Redstone block',7:'Observer',8:'Rod',9:'Piston',10:'Piston arm'};
const directions = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
const dirNames = ['+X','−X','+Y','−Y','+Z','−Z'];
function orientBlock(mesh,direction) {
  const turn=Math.PI/2;
  const rotations=[[0,turn,0],[0,-turn,0],[-turn,0,0],[turn,0,0],[0,0,0],[0,Math.PI,0]];
  mesh.rotation.set(...rotations[direction]);
}
// BoxGeometry UVs rotate differently on each side. In local coordinates +Z
// is the output/front edge, so these turns keep every side detail aligned.
const sideTurns=[0,Math.PI,-Math.PI/2,Math.PI/2];
const $ = id => document.getElementById(id);
const key = p => p.join(',');
const decode = cell => ({kind:cell&15,moving:!!(cell&16),direction:(cell>>5)&7,powered:(cell&15)===7&&!!(cell&256),sticky:(cell&15)===9&&!!(cell&256),angry:(cell&15)===9&&!!(cell&512),state:(cell>>10)&3});
const short = p => `(${p.join(', ')})`;

// Small, local canvas textures: Minecraft-like material cues without bundled game assets.
const textures = new Map();
function faceTexture(style) {
  if(textures.has(style)) return textures.get(style);
  const canvas=document.createElement('canvas');canvas.width=64;canvas.height=64;
  const ctx=canvas.getContext('2d');
  const fill=(color,x,y,w,h)=>{ctx.fillStyle=color;ctx.fillRect(x,y,w,h);};
  const frame=(outer,inner)=>{fill(outer,0,0,64,64);fill(inner,5,5,54,54);};
  if(style==='arm') {
    frame('#5d5b51','#b99369');
    fill('#d5b486',10,10,44,7);fill('#816443',10,26,44,6);
    fill('#c5a077',10,38,44,16);
  } else if(style==='rod-shaft') {
    fill('#9d7842',0,0,64,64);
    fill('#d2ad69',6,0,13,64);fill('#ead08d',21,0,7,64);
    fill('#84613a',42,0,9,64);fill('#c89f5f',54,0,8,64);
    fill('#755c3c',0,10,64,5);fill('#e4bf78',0,15,64,4);
    fill('#755c3c',0,48,64,5);fill('#e4bf78',0,53,64,4);
  } else if(style==='rod-base') {
    frame('#514b3d','#a68754');
    fill('#cfaa69',10,10,44,8);fill('#6a5840',10,40,44,10);
    fill('#dfbc79',19,21,26,17);
  }
  // Fine pixel variation keeps the surfaces legible without visual noise.
  for(let y=0;y<64;y+=8)for(let x=0;x<64;x+=8) {
    const hash=(x*17+y*31+style.length*19)%13;
    if(hash===0){ctx.fillStyle='rgba(255,255,255,.055)';ctx.fillRect(x,y,8,8);}
    if(hash===7){ctx.fillStyle='rgba(0,0,0,.045)';ctx.fillRect(x,y,8,8);}
  }
  const texture=new THREE.CanvasTexture(canvas);
  texture.magFilter=THREE.NearestFilter;texture.minFilter=THREE.NearestFilter;
  texture.colorSpace=THREE.SRGBColorSpace;
  textures.set(style,texture);return texture;
}
function headTexture(sticky) {
  const id=`head:${Number(sticky)}`;
  if(textures.has(id))return textures.get(id);
  const canvas=document.createElement('canvas');canvas.width=64;canvas.height=64;
  const ctx=canvas.getContext('2d');
  const fill=(color,x,y,w,h)=>{ctx.fillStyle=color;ctx.fillRect(x,y,w,h);};
  fill('#6b543d',0,0,64,64);
  fill('#bd9362',5,5,54,54);
  fill('#dfb980',11,11,42,42);
  fill(sticky?'#4e9b5c':'#b88b55',17,17,30,30);
  fill(sticky?'#8bd794':'#e8c487',21,21,22,22);
  const texture=new THREE.CanvasTexture(canvas);
  texture.magFilter=THREE.NearestFilter;texture.minFilter=THREE.NearestFilter;
  texture.colorSpace=THREE.SRGBColorSpace;
  textures.set(id,texture);return texture;
}
function pistonTexture(face,block,powered) {
  const id=`piston:${face}:${Number(block.sticky)}:${Number(powered)}:${Number(block.angry)}:${block.state}`;
  if(textures.has(id))return textures.get(id);
  const canvas=document.createElement('canvas');canvas.width=64;canvas.height=64;
  const ctx=canvas.getContext('2d');
  const fill=(color,x,y,w,h)=>{ctx.fillStyle=color;ctx.fillRect(x,y,w,h);};
  if(face<4){ctx.translate(32,32);ctx.rotate(sideTurns[face]);ctx.translate(-32,-32);}
  fill('#3e4945',0,0,64,64);
  fill('#87948a',5,5,54,54);
  if(face==='front') {
    fill('#a87849',8,8,48,48);
    fill('#ddba80',13,13,38,38);
    if(block.sticky) {
      fill('#387c48',19,19,26,26);
      fill('#77cf81',22,22,20,20);
    } else {
      fill('#bd8e58',19,19,26,26);
      fill('#e8c28a',22,22,20,20);
    }
  } else if(face<4) {
    // The front head slice belongs to the cube only when fully retracted.
    if(block.state===0){
      fill('#ac7e4e',5,5,13,54);
      fill(block.sticky?'#79d587':'#d7b37b',5,5,7,54);
    }else if(block.sticky)fill('#79d587',49,19,5,23);
    fill('#53615a',18,28,40,7);
  } else if(face==='interior') {
    fill('#59675e',5,5,54,54);
    fill('#33473e',23,23,18,18);
  } else {
    fill('#59675e',11,11,42,42);
    fill('#aeb8a8',19,19,26,26);
  }
  if(face<4) {
    // Built-in status strips stay on the piston as it rotates: green is sticky,
    // gold is powered, red is angry, and one of four teeth marks its state.
    fill(powered?'#f6d86f':'#596159',22,10,14,5);
    fill(block.angry?'#f26c63':'#596159',41,10,14,5);
    for(let i=0;i<4;i++)fill(i===block.state?'#f3e0ab':'#657168',22+i*9,46,6,6);
  } else if(face==='front') {
    fill(powered?'#f4d66a':'#56635d',6,6,11,6);
    fill(block.angry?'#eb665d':'#56635d',47,6,11,6);
    for(let i=0;i<4;i++)fill(i===block.state?'#e9d3a1':'#56635d',19+i*7,50,5,5);
  }
  const texture=new THREE.CanvasTexture(canvas);
  texture.magFilter=THREE.NearestFilter;texture.minFilter=THREE.NearestFilter;
  texture.colorSpace=THREE.SRGBColorSpace;
  textures.set(id,texture);return texture;
}
function observerTexture(face,powered) {
  const id=`observer:${face}:${Number(powered)}`;
  if(textures.has(id))return textures.get(id);
  const canvas=document.createElement('canvas');canvas.width=64;canvas.height=64;
  const ctx=canvas.getContext('2d');
  const fill=(color,x,y,w,h)=>{ctx.fillStyle=color;ctx.fillRect(x,y,w,h);};
  if(face<4){ctx.translate(32,32);ctx.rotate(sideTurns[face]);ctx.translate(-32,-32);}
  fill('#343c40',0,0,64,64);fill('#68757a',4,4,56,56);
  for(let y=8;y<56;y+=12)for(let x=8+(y%24?4:0);x<56;x+=16){
    fill('#829095',x,y,12,7);fill('#4a565c',x,y+7,12,2);
  }
  if(face===4) {
    // +Z is the redstone output, not the detecting face.
    fill('#343d42',8,8,48,48);fill('#a4b1b0',12,12,40,40);
    fill('#30383b',17,17,30,30);fill(powered?'#f0524b':'#713b3e',20,20,24,24);
    fill(powered?'#ffaba0':'#a16a69',25,25,14,14);
    for(const x of [7,51])for(const y of [7,51])fill('#c0c7bf',x,y,6,6);
  } else if(face===5) {
    fill('#3b4447',8,8,48,48);fill('#b0bbb7',12,12,40,40);
    fill('#4a5659',16,18,32,28);
    fill('#d2d9d0',19,20,26,22);
    fill('#30393e',20,25,9,9);fill('#30393e',35,25,9,9);
    fill('#7e999b',23,26,3,3);fill('#7e999b',38,26,3,3);
    fill('#536264',24,38,16,4);
  } else {
    // Arrow points toward local +Z, the observer's redstone power source.
    fill('#354044',8,13,48,38);fill('#8a999a',11,16,42,32);
    fill(powered?'#ff6154':'#45575d',11,28,36,8);
    fill(powered?'#ffd0b3':'#819195',11,28,30,3);
    ctx.fillStyle=powered?'#ff6154':'#45575d';
    ctx.beginPath();ctx.moveTo(8,32);ctx.lineTo(27,18);ctx.lineTo(27,46);ctx.closePath();ctx.fill();
    fill('#425055',48,22,6,20);
  }
  const texture=new THREE.CanvasTexture(canvas);
  texture.magFilter=THREE.NearestFilter;texture.minFilter=THREE.NearestFilter;
  texture.colorSpace=THREE.SRGBColorSpace;
  textures.set(id,texture);return texture;
}
function plainTexture(kind) {
  const id=`plain:${kind}`;
  if(textures.has(id))return textures.get(id);
  const canvas=document.createElement('canvas');canvas.width=64;canvas.height=64;
  const ctx=canvas.getContext('2d');
  const fill=(color,x,y,w,h)=>{ctx.fillStyle=color;ctx.fillRect(x,y,w,h);};
  const palettes={
    1:['#70c979','#97e5a0','#429755'],2:['#dcae5d','#f0ce87','#ad7b39'],
    3:['#9ca5a4','#c1c9c4','#707b79'],4:['#83c3ca','#d5f5ed','#438e9a'],
    5:['#a38bc2','#d0b2dc','#70568f'],6:['#b64748','#e36e63','#842b34'],
  };
  const [base,light,dark]=palettes[kind];fill(base,0,0,64,64);
  for(let y=0;y<64;y+=8)for(let x=0;x<64;x+=8){
    const hash=(x*13+y*19+kind*29)%11;
    if(kind!==1&&kind!==2&&hash===0)fill(light,x,y,8,8);
    if(kind!==1&&kind!==2&&hash===8)fill(dark,x,y,8,8);
  }
  if(kind===1){
    // Keep slime close to the original plain-green look.
    fill('#79d382',4,4,56,56);
    fill('#8bdc94',8,8,48,5);
    fill('#6ac674',0,58,64,6);
  } else if(kind===2){
    // Same low-detail pattern as slime, in honey colours.
    fill('#e3bc70',4,4,56,56);
    fill('#f0cd82',8,8,48,5);
    fill('#d4a95e',0,58,64,6);
  } else if(kind===3){
    fill('#6c7877',0,0,64,5);fill('#cbd1cb',4,5,56,5);
    fill('#737e7c',0,58,64,6);fill('#d0d5cf',10,18,34,4);
  } else if(kind===4){
    fill('#e1f8f0',0,0,64,6);fill('#e1f8f0',0,0,6,64);
    fill('#417f8a',58,5,6,59);fill('#417f8a',5,58,59,6);
    fill('#f2fffa',11,11,24,5);fill('#b3ece6',11,16,5,20);
  } else if(kind===5){
    fill('#694f83',0,0,64,5);fill('#dbbee5',5,5,54,5);
    fill('#795b95',0,59,64,5);fill('#76598f',7,30,50,5);
    fill('#dbbee5',28,11,8,42);fill('#e5c5e5',11,26,42,8);
    fill('#75558b',23,22,18,20);fill('#d4aede',27,26,10,12);
  } else if(kind===6){
    fill('#792a31',0,0,64,5);fill('#e57a6a',5,5,54,5);
    fill('#8c3137',0,58,64,6);fill('#f08a75',11,16,14,8);
    fill('#8b2e35',35,31,20,9);fill('#f58b75',20,45,18,6);
  }
  const texture=new THREE.CanvasTexture(canvas);
  texture.magFilter=THREE.NearestFilter;texture.minFilter=THREE.NearestFilter;
  texture.colorSpace=THREE.SRGBColorSpace;
  textures.set(id,texture);return texture;
}
function movingTexture(base) {
  const id=`moving:${base.uuid}`;
  if(textures.has(id))return textures.get(id);
  const canvas=document.createElement('canvas');canvas.width=base.image.width;canvas.height=base.image.height;
  const ctx=canvas.getContext('2d');
  ctx.drawImage(base.image,0,0);
  ctx.fillStyle='rgba(255,255,255,.5)';
  ctx.fillRect(0,0,canvas.width,canvas.height);
  const texture=new THREE.CanvasTexture(canvas);
  texture.magFilter=THREE.NearestFilter;texture.minFilter=THREE.NearestFilter;
  texture.colorSpace=THREE.SRGBColorSpace;
  textures.set(id,texture);return texture;
}
function displayedTexture(base,moving) {return moving?movingTexture(base):base;}
function faceMaterials(block,powered=false) {
  const observer=block.kind===7;
  return [0,1,2,3,4,5].map(index=>standardMaterial(
    displayedTexture(observer?observerTexture(index,block.powered)
      :pistonTexture(index===4?(block.state===0?'front':'interior'):index===5?'back':index,block,powered),block.moving),.84));
}

let trace = null, stepIndex = 0, tickIndex = 0, playbackMode = 'ticks';
let selected = null, playing = false, direction = 1, sourceBytes = null, sourceTitle = '';
let history = [], frontier = 0, detailTrace = null, detailBase = 0, playbackAccumulator = 0;
let allBounds = {min:[-2,-1,-2],max:[5,4,2]};
let startBounds = allBounds;
const scene = new THREE.Scene();
scene.background = null;
const camera = new THREE.PerspectiveCamera(47,1,.1,2000);
camera.rotation.order='YXZ';
let cameraMoveScale=1;
const renderer = new THREE.WebGLRenderer({antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.setSize(600,500);
$('canvas').appendChild(renderer.domElement);
renderer.domElement.tabIndex=0;
const ambient = new THREE.AmbientLight(0xffffff,2.2); scene.add(ambient);
const light = new THREE.DirectionalLight(0xffffff,2.2); light.position.set(-5,12,8); scene.add(light);
const content = new THREE.Group(); scene.add(content);
let ground = null;
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
let pickables = [];
const geometryCache=new Map(),materialCache=new Map();
const sharedGeometries=new Set(),sharedMaterials=new Set();
function geometry(id,create){
  if(!geometryCache.has(id)){const value=create();geometryCache.set(id,value);sharedGeometries.add(value);}
  return geometryCache.get(id);
}
function standardMaterial(texture,roughness=.84,options={}){
  const id=`${texture.uuid}:${roughness}:${options.transparent||false}:${options.opacity??1}:${options.metalness??0}`;
  if(!materialCache.has(id)){
    const value=new THREE.MeshStandardMaterial({map:texture,roughness,...options});
    materialCache.set(id,value);sharedMaterials.add(value);
  }
  return materialCache.get(id);
}
function colorMaterial(color,roughness=.75){
  const id=`color:${color.getHexString()}:${roughness}`;
  if(!materialCache.has(id)){
    const value=new THREE.MeshStandardMaterial({color,roughness});
    materialCache.set(id,value);sharedMaterials.add(value);
  }
  return materialCache.get(id);
}
function box(w=1,h=1,d=1){return geometry(`box:${w}:${h}:${d}`,()=>new THREE.BoxGeometry(w,h,d));}

function clearContent() {
  while (content.children.length) {
    const object=content.children[0]; content.remove(object);
    object.traverse(o=>{if(o.geometry&&!sharedGeometries.has(o.geometry))o.geometry.dispose(); if(o.material){const materials=Array.isArray(o.material)?o.material:[o.material];materials.forEach(m=>{if(!sharedMaterials.has(m))m.dispose();});}});
  }
  pickables=[];
}
function frameCamera() {
  cameraVelocity.set(0,0,0);
  const center = startBounds.min.map((v,i)=>(v+startBounds.max[i])/2);
  const span = Math.max(...startBounds.max.map((v,i)=>v-startBounds.min[i]),4);
  cameraMoveScale=Math.max(1,span*.45);
  const distance=Math.max(7,span*1.5);
  camera.position.set(center[0]+distance*.85,center[1]+distance*.65,center[2]+distance*.9);
  camera.lookAt(...center);
}
function computeBounds(data) {
  const min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
  const visit=row=>{for(let i=0;i<3;i++){min[i]=Math.min(min[i],row[i]);max[i]=Math.max(max[i],row[i]);}};
  data.initial.forEach(visit);
  for(const step of data.steps) step.changes.forEach(visit);
  if(!Number.isFinite(min[0])) return {min:[-2,-1,-2],max:[2,1,2]};
  return {min:min.map(v=>v-1),max:max.map(v=>v+1)};
}
function stateAt(index) {
  const cells=new Map(trace.initial.map(([x,y,z,cell])=>[key([x,y,z]),cell]));
  let owners=trace.initial_owners;
  let arms=trace.initial_arms||[];
  for(let i=0;i<index;i++) {
    const step=trace.steps[i];
    for(const [x,y,z,cell] of step.changes) {
      const id=key([x,y,z]); if(cell===null) cells.delete(id); else cells.set(id,cell);
    }
    owners=step.owners;
    arms=step.arms||[];
  }
  return {cells,owners,arms,info:index?trace.steps[index-1]:null};
}
function point(p) {return new THREE.Vector3(p[0],p[1],p[2]);}
function boxOutline(pos,color,size=1.06,opacity=1) {
  const edge=new THREE.EdgesGeometry(box(size,size,size));
  const lines=new THREE.LineSegments(edge,new THREE.LineBasicMaterial({color,transparent:opacity<1,opacity,depthTest:false}));
  lines.position.copy(point(pos)); content.add(lines);
  return lines;
}
function line(from,to,color,opacity=.9) {
  const a=point(from),b=point(to),direction=b.clone().sub(a),distance=direction.length();
  if(distance<.01)return;
  const arrow=new THREE.ArrowHelper(direction.normalize(),a,distance,color,Math.min(.18,distance*.24),.08);
  arrow.line.material.transparent=true;arrow.line.material.opacity=opacity;
  arrow.cone.material.transparent=true;arrow.cone.material.opacity=opacity;
  content.add(arrow);
}
function pickable(mesh,pos) {mesh.userData.pos=pos;pickables.push(mesh);return mesh;}
function headMaterials(sticky,moving) {
  return [0,1,2,3,4,5].map(index=>standardMaterial(
    displayedTexture(index===0?headTexture(sticky):faceTexture('arm'),moving)));
}
function makeArm(pos,block,direction,sticky=false) {
  const movingHighlight=playbackMode==='detailed'&&block.moving;
  if(direction===undefined) {
    const mesh=pickable(new THREE.Mesh(box(.78,.78,.78),
      standardMaterial(displayedTexture(faceTexture('arm'),block.moving))),pos);
    mesh.position.copy(point(pos));content.add(mesh);
    return;
  }
  const group=new THREE.Group();group.position.copy(point(pos));
  group.quaternion.setFromUnitVectors(new THREE.Vector3(1,0,0),point(directions[direction]));
  const wood=standardMaterial(displayedTexture(faceTexture('arm'),block.moving));
  const metalColor=new THREE.Color(0x77827f);
  if(block.moving)metalColor.lerp(new THREE.Color(0xffffff),.5);
  const metal=colorMaterial(metalColor);
  const shaft=pickable(new THREE.Mesh(box(1.07,.25,.25),wood),pos);shaft.position.x=-.285;group.add(shaft);
  const plate=pickable(new THREE.Mesh(box(.17,1,1),headMaterials(sticky,block.moving)),pos);
  plate.position.x=.33;group.add(plate);
  const collar=pickable(new THREE.Mesh(box(.13,.43,.43),metal),pos);
  collar.position.x=-.32;group.add(collar);
  content.add(group);
  if(movingHighlight)boxOutline(pos,0x7be4f4,1.02,.85);
}
function makeHalfwayHead(pos,block) {
  const group=new THREE.Group();group.position.copy(point(pos));
  group.quaternion.setFromUnitVectors(new THREE.Vector3(1,0,0),point(directions[block.direction]));
  const wood=standardMaterial(displayedTexture(faceTexture('arm'),block.moving));
  const shaft=pickable(new THREE.Mesh(box(.74,.24,.24),wood),pos);
  shaft.position.x=.46;group.add(shaft);
  const plate=pickable(new THREE.Mesh(box(.18,1,1),headMaterials(block.sticky,block.moving)),pos);
  plate.position.x=.91;group.add(plate);
  content.add(group);
}
function makeRod(pos,block) {
  const movingHighlight=playbackMode==='detailed'&&block.moving;
  const group=new THREE.Group();group.position.copy(point(pos));
  group.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),point(directions[block.direction]));
  const brass=standardMaterial(displayedTexture(faceTexture('rod-shaft'),block.moving),.38,{metalness:.45});
  const dark=standardMaterial(displayedTexture(faceTexture('rod-base'),block.moving),.55,{metalness:.25});
  const base=pickable(new THREE.Mesh(box(.55,.19,.55),dark),pos);base.position.y=-.34;group.add(base);
  const shaft=pickable(new THREE.Mesh(geometry('rod-shaft',()=>new THREE.CylinderGeometry(.095,.12,.64,8)),brass),pos);shaft.position.y=.02;group.add(shaft);
  const tip=pickable(new THREE.Mesh(geometry('rod-tip',()=>new THREE.CylinderGeometry(.16,.12,.16,8)),brass),pos);tip.position.y=.38;group.add(tip);
  content.add(group);
  if(movingHighlight)boxOutline(pos,0x7be4f4,1.02,.85);
}
function makeBlock(pos,cell,arms,armStickiness,powered=false) {
  const block=decode(cell);
  if(block.kind===10) {makeArm(pos,block,arms.get(key(pos)),armStickiness.get(key(pos))||false);return;}
  if(block.kind===8) {makeRod(pos,block);return;}
  const material=[7,9].includes(block.kind)?faceMaterials(block,powered&&!block.moving):standardMaterial(displayedTexture(plainTexture(block.kind),block.moving),.73,{metalness:.03,transparent:block.kind===4,opacity:block.kind===4?.48:1});
  const shortened=block.kind===9&&block.state!==0;
  const depth=shortened ? .75 : 1;
  const mesh=new THREE.Mesh(box(1,1,depth),material);
  if([7,9].includes(block.kind))orientBlock(mesh,block.direction);
  mesh.position.copy(point(pos));content.add(mesh);pickable(mesh,pos);
  if(shortened)mesh.position.addScaledVector(point(directions[block.direction]),-.125);
  const movingHighlight=playbackMode==='detailed'&&block.moving;
  const outline=new THREE.LineSegments(geometry(`block-outline:${depth}`,()=>new THREE.EdgesGeometry(box(1.002,1.002,depth+.002))),new THREE.LineBasicMaterial({color:movingHighlight?0x7be4f4:0x19242a,transparent:true,opacity:movingHighlight?1:.45}));
  outline.position.copy(mesh.position);outline.rotation.copy(mesh.rotation);content.add(outline);
}
function makeBulkBlocks(entries) {
  if(!entries.length)return;
  const groups=new Map();
  for(const [pos,cell] of entries) {
    const block=decode(cell), id=`${block.kind}-${block.moving}`;
    if(!groups.has(id))groups.set(id,[]);
    groups.get(id).push([pos,block]);
  }
  const cube=box(),dummy=new THREE.Object3D();
  for(const group of groups.values()) {
    const block=group[0][1];
    const movingHighlight=playbackMode==='detailed'&&block.moving;
    const material=standardMaterial(displayedTexture(plainTexture(block.kind),block.moving),.73,{metalness:.03,transparent:block.kind===4,opacity:block.kind===4?.48:1});
    const mesh=new THREE.InstancedMesh(cube,material,group.length);
    mesh.userData.positions=group.map(([pos])=>pos);
    group.forEach(([pos],i)=>{dummy.position.copy(point(pos));dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);});
    mesh.instanceMatrix.needsUpdate=true;content.add(mesh);pickables.push(mesh);
    if(movingHighlight)for(const [pos] of group)boxOutline(pos,0x7be4f4,1.02,.85);
  }
}
function addGround() {
  if(!ground){
    const material=new THREE.ShaderMaterial({transparent:true,depthWrite:false,side:THREE.DoubleSide,
      uniforms:{cameraPositionWorld:{value:camera.position},strength:{value:.25}},
      vertexShader:'varying vec3 worldPoint; void main(){worldPoint=(modelMatrix*vec4(position,1.0)).xyz;gl_Position=projectionMatrix*viewMatrix*vec4(worldPoint,1.0);}',
      fragmentShader:'varying vec3 worldPoint;uniform vec3 cameraPositionWorld;uniform float strength;void main(){vec2 p=worldPoint.xz;vec2 d=abs(fract(p+0.5)-0.5)/max(fwidth(p),vec2(0.001));float grid=1.0-min(min(d.x,d.y),1.0);float fade=1.0-smoothstep(18.0,85.0,length(p-cameraPositionWorld.xz));gl_FragColor=vec4(0.25,0.42,0.46,grid*fade*strength);}' });
    ground=new THREE.Mesh(new THREE.PlaneGeometry(240,240),material);
    ground.rotation.x=-Math.PI/2;
    scene.add(ground);
  }
  ground.material.uniforms.strength.value=playbackMode==='detailed'?.45:.25;
  ground.position.set(camera.position.x,allBounds.min[1]-.55,camera.position.z);
}
function addChunks(info) {
  if(!$('show-chunks').checked)return;
  const chunks=info?.chunk_order?.length?info.chunk_order:[[0,0]];
  const y=allBounds.min[1]-.52;
  const active=info?.active_chunk;
  for(const [cx,cz] of chunks) {
    const x=cx*16-trace.phase_x-.5,z=cz*16-trace.phase_z-.5;
    const activeHere=active&&active[0]===cx&&active[1]===cz;
    const points=[new THREE.Vector3(x,y,z),new THREE.Vector3(x+16,y,z),new THREE.Vector3(x+16,y,z+16),new THREE.Vector3(x,y,z+16),new THREE.Vector3(x,y,z)];
    const lineObj=new THREE.Line(new THREE.BufferGeometry().setFromPoints(points),new THREE.LineBasicMaterial({color:activeHere?0x62e1cf:0x63818b,transparent:true,opacity:activeHere?.9:.45}));
    content.add(lineObj);
  }
}
function allowed(pos) {
  return ['x','y','z'].every((axis,i)=>!$('slice-'+axis+'-on').checked||pos[i]===Number($('slice-'+axis).value));
}
function render() {
  if(!trace)return;
  clearContent();
  const {cells,owners,arms,info}=stateAt(stepIndex);
  const armDirections=new Map(arms.map(([pos,direction])=>[key(pos),direction]));
  const armStickiness=new Map(arms.map(([pos,direction])=>{
    const owner=pos.map((n,i)=>n-directions[direction][i]);
    const cell=cells.get(key(owner));
    return [key(pos),cell!==undefined&&decode(cell).kind===9&&decode(cell).sticky];
  }));
  const detailed=playbackMode==='detailed';
  const power=info?.power;
  const poweredPistons=new Set((power?.powered||[]).map(key));
  addGround();
  if(detailed)addChunks(info);
  const visible=[];
  const halfwayHeads=[];
  const hiddenArms=new Set();
  for(const [id,cell] of cells) {
    const block=decode(cell);
    if(block.kind!==9||![1,3].includes(block.state))continue;
    const pos=id.split(',').map(Number);
    if(allowed(pos))halfwayHeads.push([pos,block]);
    if(block.state===1) {
      const front=pos.map((n,i)=>n+directions[block.direction][i]);
      if((cells.get(key(front))&15)===10&&armDirections.get(key(front))===block.direction)hiddenArms.add(key(front));
    }
  }
  for(const [id,cell] of cells) {const pos=id.split(',').map(Number);if(allowed(pos)&&!hiddenArms.has(id))visible.push([pos,cell]);}
  makeBulkBlocks(visible.filter(([,cell])=>![7,8,9,10].includes(cell&15)));
  for(const [pos,cell] of visible)if([7,8,9,10].includes(cell&15))makeBlock(pos,cell,armDirections,armStickiness,poweredPistons.has(key(pos)));
  for(const [pos,block] of halfwayHeads)makeHalfwayHead(pos,block);
  if(detailed&&power&&$('show-power').checked) {
    for(const pos of power.hard) if(allowed(pos))boxOutline(pos,0xffd96c,1.14,.8);
    for(const pos of power.powered) if(allowed(pos))boxOutline(pos,0xf6d76e,1.2,.95);
    for(const [from,to,kind] of power.links) if(allowed(from)&&allowed(to)) line(from,to,kind==='soft'?0xe6b661:0xf7df8f,.65);
  }
  const movement=info?.movement;
  if(detailed&&movement&&$('show-move').checked) {
    for(const pos of movement.sources) if(allowed(pos))boxOutline(pos,0xfc9674,1.25,.95);
    for(const pos of movement.destinations) if(allowed(pos))boxOutline(pos,0x77deca,1.3,.8);
    for(const [from,to,kind] of movement.links) if(allowed(from)&&allowed(to))line(from,to,kind==='stick'?0xe978a7:0xffa36b,.95);
    for(const [from,to] of movement.ignored) if(allowed(from)&&allowed(to))line(from,to,0x687780,.3);
    if(movement.failure&&allowed(movement.failure.pos))boxOutline(movement.failure.pos,0xff555d,1.4,1);
  }
  if(detailed&&$('show-owners').checked) {
    for(const [owner,dest] of owners) {
      const ownerCell=cells.get(key(owner)),movedCell=cells.get(key(dest));
      if(ownerCell===undefined||movedCell===undefined||!decode(movedCell).moving)continue;
      const piston=decode(ownerCell);
      const d=directions[piston.direction],sign=piston.state===3?-1:1;
      const source=dest.map((v,i)=>v-d[i]*sign);
      if(allowed(dest))boxOutline(dest,0x67d6ef,1.36,.95);
      if(allowed(source)&&allowed(dest)) {
        boxOutline(source,0x66d7ed,.85,.42);
        line(source,dest,0x60d8ee,.95);
      }
    }
  }
  if(selected&&cells.has(key(selected))&&allowed(selected)){
    const block=decode(cells.get(key(selected)));
    if(block.kind===9&&block.state!==0){
      const pad=detailed?.16:.04;
      const outline=new THREE.LineSegments(new THREE.EdgesGeometry(box(1+pad,1+pad,.75+pad)),new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:detailed?1:.7,depthTest:false}));
      orientBlock(outline,block.direction);
      outline.position.copy(point(selected)).addScaledVector(point(directions[block.direction]),-.125);
      content.add(outline);
    }else boxOutline(selected,0xffffff,detailed?1.48:1.04,detailed?1:.7);
  }
  updatePanels(cells,owners,armDirections,info);
}
function property(name,value) {return `<div class="property"><span>${name}</span><span>${value}</span></div>`;}
function updatePanels(cells,owners,arms,info) {
  const step=info;
  $('step-badge').textContent=playbackMode==='ticks'?(tickIndex?'TICK':'INITIAL'):(step?step.stage.toUpperCase():'INITIAL');
  $('step-title').textContent=playbackMode==='ticks'?(tickIndex?`Tick ${tickIndex} complete`:'Initial configuration'):(step?step.title:'Initial configuration');
  $('step-counter').textContent=playbackMode==='ticks'?(tickIndex?`Tick ${tickIndex}`:'Initial state'):(detailTrace?`Tick ${detailBase+1} · action ${stepIndex}/${trace.steps.length}`:'Initial state');
  const cell=selected&&cells.get(key(selected));
  if(selected===null||cell===undefined) $('inspector').innerHTML='<div class="empty-inspector">Select a block to see its state, owner, and coordinates.</div>';
  else {
    const b=decode(cell);
    const ownersHere=owners.filter(([,member])=>key(member)===key(selected));
    let html=`<div class="inspector-title">${names[b.kind]}</div><div class="inspector-sub">${short(selected)}</div>`;
    html+=property('Moving',b.moving?'yes':'no');
    if([7,8,9,10].includes(b.kind)) {
      const facing=b.kind===10?arms.get(key(selected)):b.direction;
      html+=property('Facing',facing===undefined?'unknown':dirNames[facing]);
    }
    if(b.kind===7)html+=property('Powered',b.powered?'yes':'no');
    if(b.kind===9){
      const powered=!b.moving&&(info?.power?.powered||[]).some(pos=>key(pos)===key(selected));
      html+=property('Sticky',b.sticky?'yes':'no');
      html+=property('Powered',powered?'yes':'no');
      html+=property('Angry',b.angry?'yes':'no');
      html+=property('State',`${b.state} / 3`);
    }
    if(b.moving)html+=property('Owner',ownersHere.length===1?short(ownersHere[0][0]):`invalid: ${ownersHere.length} owners`);
    html+=property('Chunk',short([(selected[0]+trace.phase_x)>>4,(selected[2]+trace.phase_z)>>4]));
    $('inspector').innerHTML=html;
  }
  $('details-title').textContent='ACTION DETAILS';
  $('order-panel').hidden=playbackMode==='ticks';
  if(playbackMode==='detailed') {
    let details=step?`<div class="detail-row"><strong>Stage:</strong> ${step.stage}</div><div class="detail-row"><strong>Cell changes:</strong> ${info.changes.length}</div>`:'<div class="detail-row">No updates yet.</div>';
    if(step?.power)details+=`<div class="detail-row"><strong>Powered pistons:</strong> ${step.power.powered.length}<br><strong>Hard-powered solids:</strong> ${step.power.hard.length}</div>`;
    if(step?.movement){const m=step.movement;details+=`<div class="detail-row"><strong>Move set:</strong> ${m.sources.length} source blocks<br><strong>Destinations:</strong> ${m.destinations.length}<br><strong>Adhesion / obstruction links:</strong> ${m.links.length}</div>`;if(m.failure)details+=`<div class="detail-row failure"><strong>Failure:</strong> ${m.failure.reason} at ${short(m.failure.pos)}</div>`;}
    $('details').innerHTML=details;
  }
  let order='';
  if(step?.chunk_order?.length)order+=`<div>Chunks</div>${step.chunk_order.map((chunk,i)=>`<span class="order-chip ${step.active_chunk&&key(chunk)===key(step.active_chunk)?'active':''}">${i+1}: ${short(chunk)}</span>`).join('')}`;
  if(step?.piston_order?.length)order+=`<div style="margin-top:10px">Pistons in active chunk</div>${step.piston_order.map((pos,i)=>`<span class="order-chip ${step.active_piston&&key(pos)===key(step.active_piston)?'active':''}">${i+1}: ${short(pos)}</span>`).join('')}`;
  $('update-order').innerHTML=order||'Select a chunk or piston step.';
}
function entry(tick) {return history.find(item=>item.tick===tick);}
function showBoundary(tick,paint=true) {
  const item=entry(tick);
  if(!item)return false;
  tickIndex=tick;detailTrace=null;detailBase=tick;stepIndex=0;
  trace=shiftTrace(runEngine(item.bytes).trace,item.origin);
  allBounds=computeBounds(trace);
  if(paint)render();
  return true;
}
function ensureNext(tick,detailed=false) {
  const existing=entry(tick+1);
  if(existing&&!detailed)return {bytes:existing.bytes};
  const current=entry(tick);
  const result=runEngine(current.bytes,tick+1,true,detailed);
  if(!existing){
    const origin=current.origin.map((value,i)=>value-result.shift[i]);
    history.push({tick:tick+1,bytes:result.bytes,origin});frontier=tick+1;
    // Retain 200 previous tick states at the frontier; rewinding never resimulates them.
    while(history.length>201)history.shift();
  }
  if(detailed)result.trace=shiftTrace(result.trace,current.origin);
  return result;
}
function advanceTick(delta,paint=true) {
  const next=tickIndex+delta;
  if(next<history[0].tick)return false;
  if(delta>0)ensureNext(tickIndex);
  if(!paint){tickIndex=next;detailTrace=null;detailBase=next;stepIndex=0;return true;}
  return showBoundary(next,paint);
}
function advanceDetail(delta,paint=true) {
  if(delta>0){
    if(detailTrace&&stepIndex<detailTrace.steps.length){
      stepIndex++;
      if(stepIndex===detailTrace.steps.length)tickIndex=detailBase+1;
      if(paint)render();return true;
    }
    const base=tickIndex;
    const result=ensureNext(base,true);
    detailBase=base;detailTrace=result.trace;trace=detailTrace;stepIndex=1;
    if(stepIndex===trace.steps.length)tickIndex=base+1;
    allBounds=computeBounds(trace);if(paint)render();return true;
  }
  if(detailTrace&&stepIndex>0){
    stepIndex--;
    tickIndex=detailBase;
    if(stepIndex===0)return showBoundary(detailBase,paint);
    if(paint)render();return true;
  }
  if(tickIndex<=history[0].tick)return false;
  const base=tickIndex-1;
  const result=ensureNext(base,true);
  detailBase=base;detailTrace=result.trace;trace=detailTrace;
  stepIndex=Math.max(0,trace.steps.length-1);tickIndex=base;
  allBounds=computeBounds(trace);if(paint)render();return true;
}
function advance(delta,paint=true) {
  if(!trace)return false;
  try{return playbackMode==='ticks'?advanceTick(delta,paint):advanceDetail(delta,paint);}
  catch(error){showError(error);stopPlayback();return false;}
}
function setMode(mode) {
  playbackMode=mode;
  $('diagnostics-panel').hidden=mode!=='detailed';
  $('details-panel').hidden=mode!=='detailed';
  $('mode-ticks').classList.toggle('active',mode==='ticks');
  $('mode-detailed').classList.toggle('active',mode==='detailed');
  $('mode-ticks').setAttribute('aria-pressed',String(mode==='ticks'));
  $('mode-detailed').setAttribute('aria-pressed',String(mode==='detailed'));
  if(trace)showBoundary(tickIndex);
}
function stopPlayback() {playing=false;playbackAccumulator=0;$('play').textContent='▶';$('play').setAttribute('aria-label','Play');}
const speedStops=[.1,.15,.2,.25,.3,.4,.5,.6,.7,.8,.9,1,1.1,1.25,1.5,1.75,2,2.5,3,4,5,6,8,10,15,20,30];
function playbackSpeed() {return speedStops[Number($('speed').value)];}
function showError(error){$('status').textContent=error.message;$('status').classList.add('error');console.error(error);}
function installFlyer(bytes,title) {
  const result=runEngine(bytes);
  sourceBytes=result.bytes;sourceTitle=title;
  history=[{tick:0,bytes:result.bytes,origin:[0,0,0]}];frontier=0;tickIndex=0;
  detailTrace=null;detailBase=0;stepIndex=0;trace=shiftTrace(result.trace,[0,0,0]);selected=null;
  allBounds=computeBounds(trace);startBounds=allBounds;
  $('run-title').textContent=title;$('flyer-meta').textContent=`Push limit ${trace.push_limit} · ${trace.initial.length} blocks`;
  $('status').textContent='';$('status').classList.remove('error');
  stopPlayback();frameCamera();render();
}
async function loadUrl(url,title) {
  $('status').textContent='Loading flyer…';
  try{const response=await fetch(url);if(!response.ok)throw Error(`Could not load flyer (${response.status})`);installFlyer(new Uint8Array(await response.arrayBuffer()),title);}
  catch(error){showError(error);}
}
const bankBytes=new Map();
const bankVersions=new Map();
function fetchBankBytes(path){
  const version=bankVersions.get(path);
  const url=`./${path}${version?`?v=${encodeURIComponent(version)}`:''}`;
  if(!bankBytes.has(url))bankBytes.set(url,fetch(url).then(response=>{
    if(!response.ok)throw Error(`Could not load flyer (${response.status})`);
    return response.arrayBuffer().then(buffer=>new Uint8Array(buffer));
  }).catch(error=>{bankBytes.delete(url);throw error;}));
  return bankBytes.get(url);
}
const previewColors={
  1:['#8fdd9a','#5fbf72','#3c9658'],2:['#efd08c','#d9a958','#b7833b'],
  3:['#c5cbc8','#949e9a','#707b78'],4:['#b7e5e6','#80bfc7','#5e9ea9'],
  5:['#d8b9e2','#a884bc','#775e96'],6:['#ed8377','#b7494b','#8c3037'],
  7:['#bac7c8','#798b8e','#4b5e64'],8:['#e2c37b','#b48d4c','#80683d'],
  9:['#d9be91','#9c917d','#677773'],10:['#d6b88b','#aa835c','#80654a'],
};
function drawPreview(canvas,rows){
  canvas.width=108;canvas.height=70;
  const ctx=canvas.getContext('2d');
  ctx.fillStyle='#14252a';ctx.fillRect(0,0,108,70);
  if(!rows.length)return;
  const shapes=[],points=[];
  const sorted=[...rows].sort((a,b)=>(a[0]+a[1]+a[2])-(b[0]+b[1]+b[2]));
  for(const [x,y,z,cell] of sorted){
    const u=x-z,v=(x+z)*.5-y;
    const colors=previewColors[cell&15]||previewColors[3];
    const faces=[
      [[[u,v-1],[u+1,v-.5],[u,v],[u-1,v-.5]],colors[0]],
      [[[u-1,v-.5],[u,v],[u,v+1],[u-1,v+.5]],colors[1]],
      [[[u,v],[u+1,v-.5],[u+1,v+.5],[u,v+1]],colors[2]],
    ];
    for(const face of faces){shapes.push(face);points.push(...face[0]);}
  }
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  for(const [px,py] of points){minX=Math.min(minX,px);maxX=Math.max(maxX,px);minY=Math.min(minY,py);maxY=Math.max(maxY,py);}
  const scale=Math.min(98/Math.max(maxX-minX,1),60/Math.max(maxY-minY,1));
  const ox=(108-(maxX-minX)*scale)/2,oy=(70-(maxY-minY)*scale)/2;
  for(const [vertices,color] of shapes){
    ctx.beginPath();vertices.forEach(([vx,vy],i)=>{const px=ox+(vx-minX)*scale,py=oy+(vy-minY)*scale;i?ctx.lineTo(px,py):ctx.moveTo(px,py);});
    ctx.closePath();ctx.fillStyle=color;ctx.fill();ctx.strokeStyle='#1b2a2d';ctx.lineWidth=.5;ctx.stroke();
  }
}
async function loadBank() {
  const response=await fetch('./bank.json?v=__BANK_HASH__');
  if(!response.ok)throw Error(`Could not load flyer bank (${response.status})`);
  const items=await response.json();
  for(const item of items)bankVersions.set(item.path,item.version);
  // Push-limit range comes from the manifest (each flyer's own push_limit, regenerated on every build),
  // so adding a flyer at a new limit extends the filters and chart without editing this file.
  const limits=[...new Set(items.map(item=>item.push_limit))].sort((a,b)=>a-b);
  const resetRange=()=>{if(!limits.length)return;$('bank-min').value=String(limits[0]);$('bank-max').value=String(limits.at(-1));};
  for(const id of ['bank-min','bank-max'])$(id).innerHTML=limits.map(limit=>`<option value="${limit}">${limit}</option>`).join('');
  resetRange();
  const list=$('bank-list');
  const previews=new Map();
  const categoryNames={pushing_only:'Pushing-only',pulling_only:'Pulling-only',observer_only:'Observer-only',no_observer:'No observers'};
  const filterTags=[['filter-pushing','pushing_only'],['filter-pulling','pulling_only'],['filter-observer','observer_only'],['filter-no-observer','no_observer']];
  const formatSpeed=value=>Number(value.toFixed(3)).toString();
  async function openFlyer(item){
    try{
      installFlyer(await fetchBankBytes(item.path),item.name);
      $('bank-dialog').close();
    }catch(error){$('bank-summary').textContent=error.message;showError(error);}
  }
  const previewObserver=new IntersectionObserver(entries=>{
    for(const entry of entries){
      if(!entry.isIntersecting)continue;
      previewObserver.unobserve(entry.target);
      const canvas=entry.target;
      const path=canvas.dataset.path;
      const previewKey=`${path}:${bankVersions.get(path)}`;
      if(!previews.has(previewKey))previews.set(previewKey,fetchBankBytes(path).then(bytes=>runEngine(bytes).trace.initial));
      previews.get(previewKey).then(rows=>drawPreview(canvas,rows))
        .catch(error=>{canvas.title=`Preview unavailable: ${error.message}`;});
    }
  },{root:list,rootMargin:'80px'});
  function update(){
    const min=Number($('bank-min').value),max=Number($('bank-max').value);
    const search=$('bank-search').value.trim().toLowerCase();
    const tags=filterTags.filter(([id])=>$(id).checked).map(([,tag])=>tag);
    const filtered=items.filter(item=>item.push_limit>=min&&item.push_limit<=max
      &&(!search||`${item.name} ${item.path}`.toLowerCase().includes(search))
      &&tags.every(tag=>item.categories?.includes(tag)));
    const sort=$('bank-sort').value;
    filtered.sort((a,b)=>{
      const primary=sort==='speed'?(b.speed_bps??-Infinity)-(a.speed_bps??-Infinity)
        :sort==='blocks'?a.blocks-b.blocks:sort==='limit'?a.push_limit-b.push_limit:a.name.localeCompare(b.name);
      return primary||a.push_limit-b.push_limit||a.blocks-b.blocks||a.path.localeCompare(b.path);
    });
    $('bank-count').textContent=`${filtered.length} of ${items.length} flyers`;
    const measured=filtered.filter(item=>item.speed_bps!==null&&item.speed_bps!==undefined);
    const top=measured.length?Math.max(...measured.map(item=>item.speed_bps)):null;
    $('bank-summary').textContent=`${items.length} machines · ${limits.length} push limits populated${limits.length?` (PL ${limits[0]}–${limits.at(-1)})`:''}${top!==null?` · best matching speed ${formatSpeed(top)} bps`:''}`;
    const chart=$('bank-chart');chart.replaceChildren();
    const chartMax=Math.max(1,top??0);
    // One column per push limit that has a flyer in the bank; limits with no match for the current filters are greyed out.
    for(const limit of limits){
      const candidates=measured.filter(item=>item.push_limit===limit);
      const best=candidates.length?Math.max(...candidates.map(item=>item.speed_bps)):null;
      const button=document.createElement('button');button.className='chart-column';button.disabled=best===null;
      button.setAttribute('aria-label',best===null?`PL ${limit}: no matching measured flyers`:`Open fastest PL ${limit} flyer: ${formatSpeed(best)} blocks per second`);
      button.title=best===null?'No matching measured flyers':`${formatSpeed(best)} bps · click to open a fastest flyer`;
      const track=document.createElement('span');track.className='chart-track';
      const fill=document.createElement('span');fill.className='chart-fill';fill.style.height=best===null?'0':`${Math.max(1,Math.max(0,best)/chartMax*100)}%`;if(best===null)fill.style.visibility='hidden';
      const value=document.createElement('span');value.className='chart-value';value.textContent=best===null?'—':formatSpeed(best);
      const caption=document.createElement('span');caption.className='chart-limit';caption.textContent=limit;
      track.append(fill,value);button.append(track,caption);
      button.onclick=()=>{const winners=candidates.filter(item=>item.speed_bps===best);openFlyer(winners[Math.floor(Math.random()*winners.length)]);};
      chart.appendChild(button);
    }
    previewObserver.disconnect();list.replaceChildren();
    if(!filtered.length){const empty=document.createElement('div');empty.className='bank-empty';empty.textContent='No flyers match these filters. Try clearing a category or widening the push-limit range.';list.appendChild(empty);}
    for(const item of filtered){
      const button=document.createElement('button');button.className='bank-item';
      const image=document.createElement('canvas');image.dataset.path=item.path;image.width=108;image.height=70;
      image.setAttribute('aria-hidden','true');
      const label=document.createElement('span');label.className='bank-copy';
      const name=document.createElement('span');name.className='bank-name';name.textContent=item.name;
      const meta=document.createElement('span');meta.className='bank-meta';meta.textContent=`PL ${item.push_limit} · ${item.blocks} blocks · ${item.speed_bps==null?'Unmeasured':`${formatSpeed(item.speed_bps)} bps`}`;
      const badges=document.createElement('span');badges.className='bank-tags';badges.textContent=(item.categories||[]).map(tag=>categoryNames[tag]).join(' · ');
      label.append(name,meta,badges);button.append(image,label);
      button.title=item.path;button.onclick=()=>openFlyer(item);
      list.appendChild(button);
      previewObserver.observe(image);
    }
  }
  for(const id of ['bank-min','bank-max','bank-sort',...filterTags.map(([id])=>id)])$(id).onchange=update;
  $('bank-search').oninput=update;
  $('bank-clear').onclick=()=>{resetRange();$('bank-search').value='';for(const [id] of filterTags)$(id).checked=false;update();};
  update();$('open-bank').disabled=false;
}
$('open-bank').disabled=true;
$('open-bank').onclick=()=>{setDisplayFocused(false);$('bank-dialog').showModal();};
$('close-bank').onclick=()=>$('bank-dialog').close();
$('bank-dialog').addEventListener('click',event=>{
  if(event.target!==$('bank-dialog'))return;
  const rect=$('bank-dialog').getBoundingClientRect();
  if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)$('bank-dialog').close();
});
$('file').onchange=async event=>{const file=event.target.files[0];if(!file)return;try{installFlyer(new Uint8Array(await file.arrayBuffer()),file.name);}catch(error){showError(error);}};
$('reset').onclick=()=>{if(!sourceBytes)return;const wasPlaying=playing;installFlyer(sourceBytes,sourceTitle);if(wasPlaying){playing=true;$('play').textContent='Ⅱ';$('play').setAttribute('aria-label','Pause');}};
$('direction').onclick=()=>{direction=-direction;$('direction').textContent=direction>0?'→':'←';$('direction').setAttribute('aria-label',`Direction: ${direction>0?'forward':'backward'}`);$('step').textContent=direction>0?'›':'‹';$('step').setAttribute('aria-label',`Step ${direction>0?'forward':'backward'}`);};
$('step').onclick=()=>advance(direction);
$('speed').oninput=()=>{const label=`${playbackSpeed()}×`;$('speed-label').textContent=label;$('speed').setAttribute('aria-valuetext',label);};
$('mode-ticks').onclick=()=>setMode('ticks');
$('mode-detailed').onclick=()=>setMode('detailed');
$('play').onclick=()=>{if(!trace)return;playing=!playing;playbackAccumulator=0;$('play').textContent=playing?'Ⅱ':'▶';$('play').setAttribute('aria-label',playing?'Pause':'Play');};
for(const id of ['show-power','show-move','show-owners','show-chunks','slice-x-on','slice-y-on','slice-z-on','slice-x','slice-y','slice-z'])$(id).addEventListener('input',render);
let drag=null;
let displayFocused=false;
const heldKeys=new Set();
function setDisplayFocused(value){
  displayFocused=value;renderer.domElement.classList.toggle('display-focused',value);
  if(!value){heldKeys.clear();cameraVelocity.set(0,0,0);}
}
renderer.domElement.addEventListener('pointerdown',event=>{
  if(event.button!==0)return;
  setDisplayFocused(true);
  renderer.domElement.focus();
  drag={x:event.clientX,y:event.clientY,startX:event.clientX,startY:event.clientY};
  renderer.domElement.setPointerCapture(event.pointerId);
});
renderer.domElement.addEventListener('pointermove',event=>{
  if(!drag)return;
  const dx=event.clientX-drag.x,dy=event.clientY-drag.y;
  drag.x=event.clientX;drag.y=event.clientY;
  // Rotate the player's view in place. The camera position never changes.
  camera.rotation.y-=dx*.015;
  camera.rotation.x=Math.max(-Math.PI/2+.02,Math.min(Math.PI/2-.02,camera.rotation.x-dy*.015));
});
renderer.domElement.addEventListener('pointerup',event=>{
  if(!drag)return;
  const wasClick=Math.abs(event.clientX-drag.startX)<=4&&Math.abs(event.clientY-drag.startY)<=4;
  drag=null;
  if(!wasClick)return;
  const rect=renderer.domElement.getBoundingClientRect();pointer.x=((event.clientX-rect.left)/rect.width)*2-1;pointer.y=-((event.clientY-rect.top)/rect.height)*2+1;
  raycaster.setFromCamera(pointer,camera);const hit=raycaster.intersectObjects(pickables)[0];selected=hit?(hit.object.userData.pos||hit.object.userData.positions?.[hit.instanceId]||null):null;render();
});
renderer.domElement.addEventListener('pointercancel',()=>{drag=null;});
renderer.domElement.addEventListener('wheel',event=>{
  if(!displayFocused)return;
  event.preventDefault();
  const forward=new THREE.Vector3();camera.getWorldDirection(forward);
  camera.position.addScaledVector(forward,-Math.sign(event.deltaY)*cameraMoveScale*.45);
},{passive:false});
const playbackControls=new Set(['reset','direction','step','play','speed','mode-ticks','mode-detailed']);
document.addEventListener('pointerdown',event=>{
  if(event.target===renderer.domElement||playbackControls.has(event.target.id))return;
  setDisplayFocused(false);renderer.domElement.blur();
},true);
window.addEventListener('keydown',event=>{
  if($('bank-dialog').open)return;
  if(event.target instanceof HTMLElement&&(event.target.matches('input, textarea, select')||event.target.isContentEditable))return;
  if(event.key==='ArrowRight'){event.preventDefault();advance(1);return;}
  if(event.key==='ArrowLeft'){event.preventDefault();advance(-1);return;}
  const keyName=event.key.toLowerCase();
  const moveKey=event.code==='Space'?'space':event.code==='ShiftLeft'||event.code==='ShiftRight'?'shift':keyName;
  if(displayFocused&&['w','a','s','d','q','e','space','shift'].includes(moveKey)){
    heldKeys.add(moveKey);
    event.preventDefault();
  }
});
window.addEventListener('keyup',event=>{
  heldKeys.delete(event.code==='Space'?'space':event.code==='ShiftLeft'||event.code==='ShiftRight'?'shift':event.key.toLowerCase());
  if(!heldKeys.size)cameraVelocity.set(0,0,0);
});
window.addEventListener('blur',()=>{heldKeys.clear();cameraVelocity.set(0,0,0);});
const cameraVelocity=new THREE.Vector3();
function moveCamera(deltaSeconds) {
  if(!heldKeys.size){cameraVelocity.set(0,0,0);return;}
  const dt=Math.min(deltaSeconds,.05);
  const forward=new THREE.Vector3();camera.getWorldDirection(forward);forward.y=0;
  if(forward.lengthSq()<.0001)forward.set(0,0,-1);
  forward.normalize();
  const right=new THREE.Vector3().crossVectors(forward,new THREE.Vector3(0,1,0)).normalize();
  const move=new THREE.Vector3();
  if(heldKeys.has('w'))move.add(forward);
  if(heldKeys.has('s'))move.sub(forward);
  if(heldKeys.has('d'))move.add(right);
  if(heldKeys.has('a'))move.sub(right);
  if(heldKeys.has('e')||heldKeys.has('space'))move.y+=1;
  if(heldKeys.has('q')||heldKeys.has('shift'))move.y-=1;
  if(move.lengthSq()>0)move.normalize().multiplyScalar(cameraMoveScale*3.6);
  cameraVelocity.lerp(move,1-Math.exp(-dt/(move.lengthSq()>.0001?.12:.018)));
  if(cameraVelocity.lengthSq()<.00001)return;
  camera.position.addScaledVector(cameraVelocity,dt);
}
function resize(){const el=$('canvas');renderer.setSize(el.clientWidth,el.clientHeight);camera.aspect=el.clientWidth/el.clientHeight;camera.updateProjectionMatrix();}
new ResizeObserver(resize).observe($('canvas'));resize();
let lastFrame=performance.now();
function animate(now){
  requestAnimationFrame(animate);
  const dt=Math.min((now-lastFrame)/1000,.1);lastFrame=now;
  moveCamera(dt);
  if(ground){ground.position.x=camera.position.x;ground.position.z=camera.position.z;}
  if(playing&&trace&&!$('bank-dialog').open){
    playbackAccumulator+=dt*10*playbackSpeed();
    let count=Math.min(Math.floor(playbackAccumulator),100);
    if(count){
      playbackAccumulator-=count;
      let changed=false;
      while(count--){if(!advance(direction,false)){stopPlayback();break;}changed=true;}
      if(changed){if(playbackMode==='ticks')showBoundary(tickIndex);else render();}
    }
  }
  renderer.render(scene,camera);
}
requestAnimationFrame(animate);
async function initialize(){
  try{await loadWasm();await Promise.all([loadBank(),loadUrl('./demo.flyer','Six-block flyer')]);}
  catch(error){showError(error);}
}
initialize();
