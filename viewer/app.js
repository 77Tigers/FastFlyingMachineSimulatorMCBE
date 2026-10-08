import * as THREE from 'three';

import {parseFlyer,serializeFlyer} from './flyer-io.js?v=__IO_HASH__';

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
    fill('#e4e5dc',0,0,64,64);
    fill('#fafaf1',5,0,19,64);fill('#c4c9c4',50,0,14,64);
  } else if(style==='rod-base') {
    frame('#8c9697','#e9ede9');
    fill('#fcfdf7',10,10,44,11);fill('#c8d0cd',10,44,44,10);
  }
  // Fine pixel variation keeps the surfaces legible without visual noise.
  for(let y=0;!style.startsWith('rod-')&&y<64;y+=8)for(let x=0;x<64;x+=8) {
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
  // Extended bases are 3/4-block deep. Crop away their missing front quarter
  // before UV mapping, keeping the status marks and frame at natural scale.
  let image=canvas;
  if(face<4&&block.state!==0){
    const cropped=document.createElement('canvas');cropped.width=64;cropped.height=64;
    const source=[[16,0,48,64],[0,0,48,64],[0,0,64,48],[0,16,64,48]][face];
    cropped.getContext('2d').drawImage(canvas,...source,0,0,64,64);
    image=cropped;
  }
  const texture=new THREE.CanvasTexture(image);
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
    // One broad frame, lots of pale face, and a readable expression.
    fill('#30393c',8,8,48,48);fill('#d6ded8',12,12,40,40);
    if(powered){
      fill('#38434a',18,20,10,12);fill('#38434a',36,20,10,12);
      fill('#eef5ec',21,22,3,3);fill('#eef5ec',39,22,3,3);
      ctx.fillStyle='#38434a';ctx.beginPath();ctx.ellipse(32,42,7,8,0,0,Math.PI*2);ctx.fill();
      fill('#b8c7c1',29,40,6,5);
      fill('#e78b83',14,37,8,4);fill('#e78b83',42,37,8,4);
    }else{
      fill('#38434a',19,25,8,8);fill('#38434a',37,25,8,8);
      fill('#8aa2a1',21,26,3,3);fill('#8aa2a1',39,26,3,3);
      fill('#536264',26,42,12,4);
    }
  } else {
    // Arrow points toward local +Z, the observer's redstone power source.
    fill('#354044',8,13,48,38);fill('#8a999a',11,16,42,32);
    // Single silhouette avoids a triangle overlapping a rectangular shaft.
    ctx.fillStyle=powered?'#ef675d':'#45575d';
    ctx.beginPath();ctx.moveTo(8,32);ctx.lineTo(27,17);ctx.lineTo(27,25);
    ctx.lineTo(53,25);ctx.lineTo(53,39);ctx.lineTo(27,39);
    ctx.lineTo(27,47);ctx.closePath();ctx.fill();
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
    3:['#9ca5a4','#c1c9c4','#707b79'],4:['#e4f3f2','#f7fffd','#c8e0e2'],
    5:['#49365e','#8d69a7','#302944'],6:['#a13d43','#c35a59','#702b35'],
  };
  const [base,light,dark]=palettes[kind];fill(base,0,0,64,64);
  for(let y=0;y<64;y+=8)for(let x=0;x<64;x+=8){
    const hash=(x*13+y*19+kind*29)%11;
    if(kind!==1&&kind!==2&&kind!==6&&hash===0)fill(light,x,y,8,8);
    if(kind!==1&&kind!==2&&kind!==6&&hash===8)fill(dark,x,y,8,8);
  }
  if(kind===1){
    // No per-block rim: touching slime cubes read as one connected mass.
    fill('#79d382',0,0,64,64);
    fill('#80d78a',12,15,22,17);
    fill('#75ce7e',35,38,19,14);
  } else if(kind===2){
    // Honey uses the same connected, borderless pattern in amber.
    fill('#e3bc70',0,0,64,64);
    fill('#e9c377',12,15,22,17);
    fill('#dcb36a',35,38,19,14);
  } else if(kind===3){
    fill('#6c7877',0,0,64,5);fill('#cbd1cb',4,5,56,5);
    fill('#737e7c',0,58,64,6);fill('#d0d5cf',10,18,34,4);
  } else if(kind===4){
    fill('#e9f6f4',0,0,64,64);
    fill('#d3e8e7',0,0,64,2);fill('#d3e8e7',0,0,2,64);
    fill('#c9e0e1',62,0,2,64);fill('#c9e0e1',0,62,64,2);
    fill('#fbfffe',12,12,20,3);fill('#f4fffd',12,15,3,17);
  } else if(kind===5){
    // Dark-purple glazed-terracotta-inspired quarter spirals.
    fill('#34283f',0,0,64,64);
    fill('#5d4375',5,5,54,54);
    fill('#332940',10,10,44,44);
    fill('#8e6da3',10,10,31,7);fill('#8e6da3',10,10,7,31);
    fill('#a783b6',23,22,30,7);fill('#a783b6',46,22,7,30);
    fill('#75558c',22,35,30,7);fill('#75558c',22,35,7,18);
    fill('#c29dc9',28,27,8,8);
    fill('#4a335c',5,46,15,13);fill('#4a335c',44,5,15,13);
  } else if(kind===6){
    // Interlocking redstone tiles, with no horizontal banding.
    fill('#97383e',0,0,64,64);
    fill('#b64a4c',5,6,21,21);fill('#c35755',30,4,26,15);
    fill('#7e3039',40,20,18,19);fill('#a94144',7,34,26,23);
    fill('#c65956',33,42,22,15);fill('#d0675e',17,17,11,11);
    fill('#762c35',28,26,12,14);fill('#d06b61',47,24,8,8);
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
  ctx.fillStyle='rgba(255,255,255,.10)';
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
let movingDisplayMode='smooth',motionFrameKey='',motionStartedAt=0,motionDuration=500,motionTargetProgress=1,motionDirection=1,manualStepRendering=false;
const movingVisuals=[];
const pistonHeadVisuals=[];
const movingFlashMaterials=new Set();
let selected = null, playing = false, direction = 1, sourceBytes = null, sourceTitle = '';
let sourceOrigin=[0,0,0],editorMode='view',editFlyer=null,selectedSlot=1;
let recentDbPromise=null,recentWrite=Promise.resolve(),restoringRecent=false;
function recentDb(){
  if(!('indexedDB' in window))return Promise.reject(Error('IndexedDB is unavailable'));
  if(!recentDbPromise)recentDbPromise=new Promise((resolve,reject)=>{
    const request=indexedDB.open('fastflyer-workspace',1);
    request.onupgradeneeded=()=>request.result.createObjectStore('recent');
    request.onsuccess=()=>{
      request.result.onversionchange=()=>{request.result.close();recentDbPromise=null;};
      resolve(request.result);
    };
    request.onerror=()=>reject(request.error);
    request.onblocked=()=>reject(Error('The local flyer cache is blocked by another tab'));
  }).catch(error=>{recentDbPromise=null;throw error;});
  return recentDbPromise;
}
async function readRecentFlyer(){
  const db=await recentDb();
  return new Promise((resolve,reject)=>{
    const request=db.transaction('recent','readonly').objectStore('recent').get('last');
    request.onsuccess=()=>resolve(request.result||null);
    request.onerror=()=>reject(request.error);
  });
}
async function writeRecentFlyer(snapshot){
  const db=await recentDb();
  return new Promise((resolve,reject)=>{
    const transaction=db.transaction('recent','readwrite');
    transaction.objectStore('recent').put(snapshot,'last');
    transaction.oncomplete=resolve;
    transaction.onerror=()=>reject(transaction.error);
    transaction.onabort=()=>reject(transaction.error);
  });
}
function rememberFlyer(){
  if(restoringRecent||!sourceBytes)return;
  const snapshot={bytes:sourceBytes.slice(),title:sourceTitle,origin:[...sourceOrigin],
    mode:editorMode,slot:selectedSlot};
  recentWrite=recentWrite.catch(()=>{}).then(()=>writeRecentFlyer(snapshot)).catch(error=>{
    console.warn('Could not save the recent flyer locally',error);
    $('status').textContent='Local autosave unavailable. Export your flyer to keep your edits.';
    $('status').classList.add('error');
  });
}
let history = [], frontier = 0, detailTrace = null, detailBase = 0, playbackAccumulator = 0;
let allBounds = {min:[-2,-1,-2],max:[5,4,2]};
let startBounds = allBounds;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x050c19);
const camera = new THREE.PerspectiveCamera(47,1,.1,2000);
camera.rotation.order='YXZ';
const flyerMiddle=new THREE.Vector3(),followAnchor=new THREE.Vector3(),followVelocity=new THREE.Vector3();
let travelOriginX=0;
// A fixed night sky, translated with the camera so it feels infinitely distant.
const sky=new THREE.Group();scene.add(sky);
const starPositions=[],starColors=[],brightPositions=[],brightColors=[];
let starSeed=0x51a7c3;
const starRandom=()=>{starSeed=(Math.imul(starSeed,1664525)+1013904223)>>>0;return starSeed/4294967296;};
for(let i=0;i<1900;i++){
  // The lower hemisphere is sky too, including below the ground grid.
  const height=-.98+starRandom()*1.96,angle=starRandom()*Math.PI*2;
  const radius=360+starRandom()*280,flat=Math.sqrt(1-height*height);
  const coordinates=[radius*flat*Math.cos(angle),radius*height,radius*flat*Math.sin(angle)];
  const glow=.35+starRandom()*.58,tint=starRandom();
  const colors=tint<.16?[glow*.88,glow*.75,glow]:tint<.33?[glow*.72,glow,glow*.98]:[glow*.91,glow*.94,glow];
  (i%13===0?brightPositions:starPositions).push(...coordinates);
  (i%13===0?brightColors:starColors).push(...colors);
}
function starPoints(positions,colors,size,opacity){
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
  return new THREE.Points(geometry,new THREE.PointsMaterial({size,sizeAttenuation:false,vertexColors:true,transparent:true,opacity,depthWrite:false}));
}
sky.add(starPoints(starPositions,starColors,1.6,.88));
sky.add(starPoints(brightPositions,brightColors,3.4,.95));
// Direction-based polar glows: no bitmap pixels, longitude seam, or UV pinch.
sky.add(new THREE.Mesh(new THREE.SphereGeometry(850,64,48),new THREE.ShaderMaterial({
  transparent:true,depthWrite:false,side:THREE.BackSide,
  vertexShader:'varying vec3 skyDirection; void main(){skyDirection=normalize(position);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
  fragmentShader:`varying vec3 skyDirection;
    void main(){
      vec3 d=normalize(skyDirection);
      float latitude=abs(d.y);
      float wave=sin(d.x*9.0+d.z*5.0)*0.033+sin(d.x*14.0-d.z*10.0)*0.018;
      float inner=exp(-pow((latitude-(0.69+wave))/0.058,2.0));
      float outer=exp(-pow((latitude-(0.79+wave*0.55))/0.046,2.0));
      float polarFade=smoothstep(0.48,0.62,latitude)*(1.0-smoothstep(0.89,0.985,latitude));
      float alpha=polarFade*(0.008+inner*0.084+outer*0.051);
      vec3 colour=d.y>0.0?vec3(0.25,0.55,0.68):vec3(0.46,0.33,0.68);
      gl_FragColor=vec4(colour,alpha);
    }`,
})));
function polarCrown(sign,latitude,color,opacity){
  const radius=650*Math.sqrt(1-latitude*latitude),height=sign*650*latitude;
  const points=Array.from({length:128},(_,i)=>{
    const angle=i/128*Math.PI*2;
    return new THREE.Vector3(radius*Math.cos(angle),height,radius*Math.sin(angle));
  });
  sky.add(new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(points),
    new THREE.LineBasicMaterial({color,transparent:true,opacity,depthWrite:false})));
}
for(const sign of [1,-1]){
  polarCrown(sign,.90,sign>0?0x68c7d4:0xb38add,.19);
  polarCrown(sign,.965,sign>0?0xa0dfdc:0xceabec,.12);
}
function polarBeacon(sign,colour){
  const canvas=document.createElement('canvas');canvas.width=128;canvas.height=128;
  const ctx=canvas.getContext('2d');
  const glow=ctx.createRadialGradient(64,64,2,64,64,56);
  glow.addColorStop(0,'rgba(245,250,255,.92)');glow.addColorStop(.14,colour);
  glow.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=glow;ctx.fillRect(0,0,128,128);
  ctx.strokeStyle='rgba(233,245,255,.60)';ctx.lineWidth=2;
  for(let i=0;i<8;i++){
    const angle=i*Math.PI/4;
    ctx.beginPath();ctx.moveTo(64+Math.cos(angle)*22,64+Math.sin(angle)*22);
    ctx.lineTo(64+Math.cos(angle)*(i%2?35:47),64+Math.sin(angle)*(i%2?35:47));ctx.stroke();
  }
  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
  const sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:texture,transparent:true,depthWrite:false,opacity:.74}));
  sprite.position.set(0,sign*660,0);sprite.scale.set(78,78,1);sky.add(sprite);
}
polarBeacon(1,'rgba(92,205,224,.52)');
polarBeacon(-1,'rgba(169,123,219,.52)');
const moonCanvas=document.createElement('canvas');moonCanvas.width=128;moonCanvas.height=128;
const moonContext=moonCanvas.getContext('2d');
moonContext.fillStyle='#d7eced';moonContext.beginPath();moonContext.arc(64,64,43,0,Math.PI*2);moonContext.fill();
moonContext.globalCompositeOperation='destination-out';moonContext.beginPath();moonContext.arc(81,51,40,0,Math.PI*2);moonContext.fill();
const moonTexture=new THREE.CanvasTexture(moonCanvas);moonTexture.colorSpace=THREE.SRGBColorSpace;
const moon=new THREE.Sprite(new THREE.SpriteMaterial({map:moonTexture,transparent:true,depthWrite:false,opacity:.83}));
moon.position.set(-195,300,-470);moon.scale.set(58,58,1);sky.add(moon);
const southCanvas=document.createElement('canvas');southCanvas.width=160;southCanvas.height=160;
const southContext=southCanvas.getContext('2d');
southContext.strokeStyle='rgba(157,129,225,.54)';southContext.lineWidth=5;
southContext.beginPath();southContext.ellipse(80,82,65,20,-.35,0,Math.PI*2);southContext.stroke();
southContext.fillStyle='#40527c';southContext.beginPath();southContext.arc(80,80,36,0,Math.PI*2);southContext.fill();
southContext.fillStyle='#7382aa';southContext.beginPath();southContext.arc(70,68,24,0,Math.PI*2);southContext.fill();
southContext.strokeStyle='rgba(205,174,247,.82)';southContext.lineWidth=4;
southContext.beginPath();southContext.ellipse(80,82,65,20,-.35,0,Math.PI);southContext.stroke();
const southTexture=new THREE.CanvasTexture(southCanvas);southTexture.colorSpace=THREE.SRGBColorSpace;
const southOrb=new THREE.Sprite(new THREE.SpriteMaterial({map:southTexture,transparent:true,depthWrite:false,opacity:.88}));
southOrb.position.set(120,-535,-160);southOrb.scale.set(94,94,1);sky.add(southOrb);
const constellationDirections=[[-.65,.57,-.50],[-.57,.63,-.53],[-.48,.55,-.68],[-.34,.69,-.64],[-.25,.6,-.76]];
const constellationPoints=constellationDirections.map(v=>new THREE.Vector3(...v).normalize().multiplyScalar(480));
const constellationGeometry=new THREE.BufferGeometry().setFromPoints(constellationPoints);
sky.add(new THREE.Line(constellationGeometry,new THREE.LineBasicMaterial({color:0x7399b1,transparent:true,opacity:.27,depthWrite:false})));
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
const frontFacingOutlines=[];
const geometryCache=new Map(),materialCache=new Map();
const sharedGeometries=new Set(),sharedMaterials=new Set();
function geometry(id,create){
  if(!geometryCache.has(id)){const value=create();geometryCache.set(id,value);sharedGeometries.add(value);}
  return geometryCache.get(id);
}
function standardMaterial(texture,roughness=.84,options={}){
  const id=`${texture.uuid}:${roughness}:${options.transparent||false}:${options.opacity??1}:${options.metalness??0}:${options.depthWrite??true}`;
  if(!materialCache.has(id)){
    const value=new THREE.MeshStandardMaterial({map:texture,roughness,...options});
    materialCache.set(id,value);sharedMaterials.add(value);
  }
  return materialCache.get(id);
}
function box(w=1,h=1,d=1){return geometry(`box:${w}:${h}:${d}`,()=>new THREE.BoxGeometry(w,h,d));}
function outlineOctant(pos){
  return (camera.position.x>=pos[0]?1:0)|(camera.position.y>=pos[1]?2:0)|(camera.position.z>=pos[2]?4:0);
}
function frontOutlineGeometry(size,octant){
  return geometry(`front-outline:${size}:${octant}`,()=>{
    const half=size/2,points=[],seen=new Set();
    for(let axis=0;axis<3;axis++){
      const other=[0,1,2].filter(value=>value!==axis),corners=[];
      for(const [a,b] of [[-1,-1],[1,-1],[1,1],[-1,1]]){
        const corner=[0,0,0];corner[axis]=(octant&(1<<axis)?1:-1)*half;
        corner[other[0]]=a*half;corner[other[1]]=b*half;corners.push(corner);
      }
      for(let i=0;i<4;i++){
        const a=corners[i],b=corners[(i+1)%4],edge=[a.join(','),b.join(',')].sort().join('|');
        if(seen.has(edge))continue;seen.add(edge);
        points.push(new THREE.Vector3(...a),new THREE.Vector3(...b));
      }
    }
    return new THREE.BufferGeometry().setFromPoints(points);
  });
}
function glassGeometry(mask){
  return geometry(`glass:${mask}`,()=>{
    const source=box(),result=new THREE.BufferGeometry(),indices=[];
    for(const name of ['position','normal','uv'])result.setAttribute(name,source.getAttribute(name));
    for(let face=0;face<6;face++)if(mask&(1<<face)){
      const group=source.groups[face];
      for(let i=group.start;i<group.start+group.count;i++)indices.push(source.index.getX(i));
    }
    result.setIndex(indices);result.computeBoundingSphere();return result;
  });
}

function clearContent() {
  while (content.children.length) {
    const object=content.children[0]; content.remove(object);
    object.traverse(o=>{if(o.geometry&&!sharedGeometries.has(o.geometry))o.geometry.dispose(); if(o.material){const materials=Array.isArray(o.material)?o.material:[o.material];materials.forEach(m=>{if(!sharedMaterials.has(m))m.dispose();});}});
  }
  pickables=[];
  frontFacingOutlines.length=0;
}
function frameCamera() {
  cameraVelocity.set(0,0,0);
  const center = startBounds.min.map((v,i)=>(v+startBounds.max[i])/2);
  const span = Math.max(...startBounds.max.map((v,i)=>v-startBounds.min[i]),4);
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
  const middle=new THREE.Vector3();
  let minimumX=Infinity;
  for(const id of cells.keys()){
    const [x,y,z]=id.split(',').map(Number);
    middle.x+=x;middle.y+=y;middle.z+=z;
    minimumX=Math.min(minimumX,x);
  }
  if(cells.size)middle.divideScalar(cells.size);
  return {cells,owners,arms,info:index?trace.steps[index-1]:null,middle,
    minimumX:Number.isFinite(minimumX)?minimumX:travelOriginX};
}
function point(p) {return new THREE.Vector3(p[0],p[1],p[2]);}
function boxOutline(pos,color,size=1.06,opacity=1) {
  const octant=outlineOctant(pos);
  const lines=new THREE.LineSegments(frontOutlineGeometry(size,octant),new THREE.LineBasicMaterial({color,transparent:opacity<1,opacity,depthTest:true,depthWrite:false}));
  lines.position.copy(point(pos)); content.add(lines);
  frontFacingOutlines.push({lines,pos,size,octant});
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
  const shaft=pickable(new THREE.Mesh(box(1.15,.25,.25),wood),pos);shaft.position.x=-.245;group.add(shaft);
  const plate=pickable(new THREE.Mesh(box(.17,1,1),headMaterials(sticky,block.moving)),pos);
  plate.position.x=.415;group.add(plate);
  content.add(group);
  if(movingHighlight)boxOutline(pos,0x7be4f4,1.02,.85);
}
function makeHalfwayHead(pos,block) {
  const group=new THREE.Group();group.position.copy(point(pos));
  group.quaternion.setFromUnitVectors(new THREE.Vector3(1,0,0),point(directions[block.direction]));
  const wood=standardMaterial(displayedTexture(faceTexture('arm'),block.moving));
  const shaft=pickable(new THREE.Mesh(box(.74,.24,.24),wood),pos);
  group.add(shaft);
  const plate=pickable(new THREE.Mesh(box(.18,1,1),headMaterials(block.sticky,block.moving)),pos);
  group.add(plate);
  content.add(group);
  pistonHeadVisuals.push({shaft,plate,state:block.state});
}
function makeRod(pos,block) {
  const movingHighlight=playbackMode==='detailed'&&block.moving;
  const group=new THREE.Group();group.position.copy(point(pos));
  group.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),point(directions[block.direction]));
  const white=standardMaterial(displayedTexture(faceTexture('rod-shaft'),block.moving),.76,{metalness:0});
  const baseMaterial=standardMaterial(displayedTexture(faceTexture('rod-base'),block.moving),.7,{metalness:0});
  const base=pickable(new THREE.Mesh(box(.42,.18,.42),baseMaterial),pos);base.position.y=-.36;group.add(base);
  const shaft=pickable(new THREE.Mesh(box(.22,.66,.22),white),pos);shaft.position.y=.02;group.add(shaft);
  const tip=pickable(new THREE.Mesh(box(.3,.12,.3),white),pos);tip.position.y=.39;group.add(tip);
  content.add(group);
  if(movingHighlight)boxOutline(pos,0x7be4f4,1.02,.85);
}
function makeBlock(pos,cell,arms,armStickiness,powered=false,glassMask=63) {
  const block=decode(cell);
  if(block.kind===10) {makeArm(pos,block,arms.get(key(pos)),armStickiness.get(key(pos))||false);return;}
  if(block.kind===8) {makeRod(pos,block);return;}
  const material=[7,9].includes(block.kind)?faceMaterials(block,powered&&!block.moving):standardMaterial(displayedTexture(plainTexture(block.kind),block.moving),.73,{metalness:.03,transparent:block.kind===4,opacity:block.kind===4?.42:1,depthWrite:block.kind!==4});
  const shortened=block.kind===9&&block.state!==0;
  const depth=shortened ? .75 : 1;
  const mesh=new THREE.Mesh(block.kind===4?glassGeometry(glassMask):box(1,1,depth),material);
  if([7,9].includes(block.kind))orientBlock(mesh,block.direction);
  mesh.position.copy(point(pos));content.add(mesh);pickable(mesh,pos);
  if(shortened)mesh.position.addScaledVector(point(directions[block.direction]),-.125);
  const movingHighlight=playbackMode==='detailed'&&block.moving;
  if([7,9].includes(block.kind)||movingHighlight){
    const outline=new THREE.LineSegments(geometry(`block-outline:${depth}`,()=>new THREE.EdgesGeometry(box(1.002,1.002,depth+.002))),new THREE.LineBasicMaterial({color:movingHighlight?0x7be4f4:0x19242a,transparent:true,opacity:movingHighlight?1:.45}));
    outline.position.copy(mesh.position);outline.rotation.copy(mesh.rotation);content.add(outline);
  }
}
function glassFaceMask(pos,cells,motionByDestination){
  let mask=63;
  const delta=motionByDestination.get(key(pos));
  for(let face=0;face<6;face++){
    const neighbor=pos.map((value,i)=>value+directions[face][i]);
    const neighborCell=cells.get(key(neighbor));
    if(neighborCell===undefined||(neighborCell&15)!==4||!allowed(neighbor))continue;
    const neighborDelta=motionByDestination.get(key(neighbor));
    if((!delta&&!neighborDelta)||(delta&&neighborDelta&&delta.equals(neighborDelta)))mask&=~(1<<face);
  }
  return mask;
}
function makeBulkBlocks(entries,cells,motionByDestination) {
  if(!entries.length)return;
  const groups=new Map();
  for(const [pos,cell] of entries) {
    const block=decode(cell);
    const mask=block.kind===4?glassFaceMask(pos,cells,motionByDestination):63;
    const id=`${block.kind}-${block.moving}-${mask}`;
    if(!groups.has(id))groups.set(id,[]);
    groups.get(id).push([pos,block,mask]);
  }
  const cube=box(),dummy=new THREE.Object3D();
  for(const group of groups.values()) {
    const block=group[0][1],mask=group[0][2];
    const movingHighlight=playbackMode==='detailed'&&block.moving;
    const material=standardMaterial(displayedTexture(plainTexture(block.kind),block.moving),.73,{metalness:.03,transparent:block.kind===4,opacity:block.kind===4?.42:1,depthWrite:block.kind!==4});
    const mesh=new THREE.InstancedMesh(block.kind===4?glassGeometry(mask):cube,material,group.length);
    mesh.userData.positions=group.map(([pos])=>pos);
    group.forEach(([pos],i)=>{dummy.position.copy(point(pos));dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);});
    mesh.instanceMatrix.needsUpdate=true;content.add(mesh);pickables.push(mesh);
    if(block.moving)trackMovingFlash([mesh]);
    if(movingHighlight)for(const [pos] of group)boxOutline(pos,0x7be4f4,1.02,.85);
  }
}
function addGround() {
  if(!ground){
    const material=new THREE.ShaderMaterial({transparent:true,depthWrite:false,side:THREE.DoubleSide,
      uniforms:{cameraPositionWorld:{value:camera.position},strength:{value:.25}},
      vertexShader:'varying vec3 worldPoint; void main(){worldPoint=(modelMatrix*vec4(position,1.0)).xyz;gl_Position=projectionMatrix*viewMatrix*vec4(worldPoint,1.0);}',
      fragmentShader:'varying vec3 worldPoint;uniform vec3 cameraPositionWorld;uniform float strength;void main(){vec2 p=worldPoint.xz;vec2 d=abs(fract(p)-0.5)/max(fwidth(p),vec2(0.001));float grid=1.0-min(min(d.x,d.y),1.0);float fade=1.0-smoothstep(18.0,85.0,length(p-cameraPositionWorld.xz));gl_FragColor=vec4(0.25,0.42,0.46,grid*fade*strength);}' });
    ground=new THREE.Mesh(new THREE.PlaneGeometry(240,240),material);
    ground.rotation.x=-Math.PI/2;
    scene.add(ground);
  }
  ground.material.uniforms.strength.value=playbackMode==='detailed'?.45:.25;
  ground.visible=$('show-floor').checked;
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
function trackMoving(objects,delta){
  for(const object of objects)movingVisuals.push({object,base:object.position.clone(),delta});
}
function trackMovingFlash(objects){
  for(const object of objects)object.traverse(child=>{
    const materials=Array.isArray(child.material)?child.material:child.material?[child.material]:[];
    for(const material of materials)if(material.isMeshStandardMaterial){
      material.emissive.set(0xffffff);movingFlashMaterials.add(material);
    }
  });
}
function updateMovingVisuals(now){
  if(!movingVisuals.length)return;
  const progress=movingDisplayMode==='halfway'?.5:motionTargetProgress*Math.min(1,(now-motionStartedAt)/motionDuration);
  const offsetFactor=motionDirection<0?progress:1-progress;
  for(const {object,base,delta} of movingVisuals)object.position.copy(base).addScaledVector(delta,offsetFactor);
}
function updatePistonHeads(now){
  if(!pistonHeadVisuals.length)return;
  const elapsed=motionTargetProgress*Math.min(1,(now-motionStartedAt)/motionDuration);
  for(const {shaft,plate,state} of pistonHeadVisuals){
    // Real preserves the old half-extended head; Halfway makes that explicit.
    const forwardProgress=motionDirection<0?1-elapsed:elapsed;
    const progress=movingDisplayMode==='smooth'?(state===1?forwardProgress:1-forwardProgress):.5;
    const plateCenter=.5+progress*.91,shaftStart=.13,shaftEnd=plateCenter-.09;
    shaft.position.x=(shaftStart+shaftEnd)/2;
    shaft.scale.x=(shaftEnd-shaftStart)/.74;
    plate.position.x=plateCenter;
  }
}
function updateMovingFlash(now){
  const phase=Math.min(1,(now-motionStartedAt)/motionDuration);
  const intensity=Math.sin(Math.PI*phase)**2*.34;
  for(const material of movingFlashMaterials)material.emissiveIntensity=intensity;
}
function render() {
  if(!trace)return;
  clearContent();
  const {cells,owners,arms,info,middle,minimumX}=stateAt(stepIndex);
  flyerMiddle.copy(middle);
  if(!detailTrace&&stepIndex===0){const item=entry(tickIndex);if(item)item.middle=middle.toArray();}
  const armDirections=new Map(arms.map(([pos,direction])=>[key(pos),direction]));
  const armStickiness=new Map(arms.map(([pos,direction])=>{
    const owner=pos.map((n,i)=>n-directions[direction][i]);
    const cell=cells.get(key(owner));
    return [key(pos),cell!==undefined&&decode(cell).kind===9&&decode(cell).sticky];
  }));
  const detailed=playbackMode==='detailed';
  const frameKey=`${playbackMode}:${tickIndex}:${stepIndex}`;
  if(frameKey!==motionFrameKey){
    motionFrameKey=frameKey;motionStartedAt=performance.now();
    motionDuration=playing&&!manualStepRendering?Math.max(45,Math.min(400,90/playbackSpeed())):500;
    motionTargetProgress=(manualStepRendering||!playing) ? .5 : 1;
  }
  // Editing rebuilds the scene after every block change. Keep in-flight
  // pistons and blocks at their paused midpoint instead of replaying them.
  if(editorMode==='edit'){
    motionTargetProgress=.5;
    motionStartedAt=performance.now()-motionDuration;
  }
  movingVisuals.length=0;
  pistonHeadVisuals.length=0;
  movingFlashMaterials.clear();
  const motionByDestination=new Map();
  if(movingDisplayMode!=='real')for(const [owner,destination] of owners){
    const ownerCell=cells.get(key(owner)),movedCell=cells.get(key(destination));
    if(ownerCell===undefined||movedCell===undefined||!decode(movedCell).moving)continue;
    const piston=decode(ownerCell),sign=piston.state===3?-1:1;
    motionByDestination.set(key(destination),point(directions[piston.direction]).multiplyScalar(-sign));
  }
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
  makeBulkBlocks(visible.filter(([pos,cell])=>![7,8,9,10].includes(cell&15)&&!motionByDestination.has(key(pos))),cells,motionByDestination);
  for(const [pos,cell] of visible)if([7,8,9,10].includes(cell&15)||motionByDestination.has(key(pos))){
    const before=content.children.length;
    makeBlock(pos,cell,armDirections,armStickiness,poweredPistons.has(key(pos)),(cell&15)===4?glassFaceMask(pos,cells,motionByDestination):63);
    const delta=motionByDestination.get(key(pos));
    if(delta)trackMoving(content.children.slice(before),delta);
    if(decode(cell).moving)trackMovingFlash(content.children.slice(before));
  }
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
      const outline=new THREE.LineSegments(new THREE.EdgesGeometry(box(1+pad,1+pad,.75+pad)),new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:detailed?1:.7,depthTest:true,depthWrite:false}));
      orientBlock(outline,block.direction);
      outline.position.copy(point(selected)).addScaledVector(point(directions[block.direction]),-.125);
      content.add(outline);
      const delta=motionByDestination.get(key(selected));if(delta)trackMoving([outline],delta);
    }else{
      const outline=boxOutline(selected,0xffffff,detailed?1.48:1.04,detailed?1:.7);
      const delta=motionByDestination.get(key(selected));if(delta)trackMoving([outline],delta);
    }
  }
  updateMovingVisuals(performance.now());
  updatePistonHeads(performance.now());
  updateMovingFlash(performance.now());
  updatePanels(cells,owners,armDirections,info,minimumX);
}
function property(name,value) {return `<div class="property"><span>${name}</span><span>${value}</span></div>`;}
function updatePanels(cells,owners,arms,info,minimumX) {
  const step=info;
  $('step-badge').textContent=playbackMode==='ticks'?(tickIndex?'TICK':'INITIAL'):(step?step.stage.toUpperCase():'INITIAL');
  $('step-title').textContent=playbackMode==='ticks'?(tickIndex?`Tick ${tickIndex} complete`:'Initial configuration'):(step?step.title:'Initial configuration');
  const progress=playbackMode==='ticks'?(tickIndex?`Tick ${tickIndex}`:'Initial state'):
    (detailTrace?`Tick ${detailBase+1} · action ${stepIndex}/${trace.steps.length}`:'Initial state');
  const travelled=Math.abs(minimumX-travelOriginX);
  $('step-counter').textContent=`${progress} · ${travelled} ${travelled===1?'block':'blocks'} travelled`;
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
  if(!trace||editorMode==='edit')return false;
  motionDirection=delta;
  manualStepRendering=paint;
  try{return playbackMode==='ticks'?advanceTick(delta,paint):advanceDetail(delta,paint);}
  catch(error){showError(error);stopPlayback();return false;}
  finally{manualStepRendering=false;}
}
function setMode(mode) {
  if(editorMode==='edit')return;
  playbackMode=mode;
  $('diagnostics-panel').hidden=mode!=='detailed';
  $('details-panel').hidden=mode!=='detailed';
  $('mode-ticks').classList.toggle('active',mode==='ticks');
  $('mode-detailed').classList.toggle('active',mode==='detailed');
  $('mode-ticks').setAttribute('aria-pressed',String(mode==='ticks'));
  $('mode-detailed').setAttribute('aria-pressed',String(mode==='detailed'));
  $('viewport-label').hidden=mode!=='detailed';
  if(trace)showBoundary(tickIndex);
}
function stopPlayback() {
  playing=false;playbackAccumulator=0;$('play').textContent='▶';$('play').setAttribute('aria-label','Play');
  // A paused in-flight state is displayed at its midpoint, not at its destination.
  motionTargetProgress=.5;motionStartedAt=performance.now()-motionDuration;
  updateMovingVisuals(performance.now());updatePistonHeads(performance.now());updateMovingFlash(performance.now());
}
const speedStops=[.1,.15,.2,.25,.3,.4,.5,.6,.7,.8,.9,1,1.1,1.25,1.5,1.75,2,2.5,3,4,5,6,8,10,15,20,30];
const playerSpeedStops=[.25,.5,.75,1,1.25,1.5,1.75,2,2.5,3];
// Preserve the old small-flyer 1× feel, independent of the flyer's dimensions.
const BASE_PLAYER_BLOCKS_PER_SECOND=9.72;
const sensitivityStops=[.1,.15,.2,.25,.3,.35,.4,.5,.6,.7,.8,.9,1,1.1,1.25,1.5,1.75,2];
const rotateSpeedStops=[.25,.5,.75,1,1.25,1.5,2,2.5,3,4];
function sliderStop(id,stops,unityIndex){
  const raw=Number($(id).value),position=Number.isFinite(raw)?Math.max(0,Math.min(100,raw))/100:.5;
  const index=position<=.5?Math.round(position*2*unityIndex):
    unityIndex+Math.round((position-.5)*2*(stops.length-1-unityIndex));
  return stops[index];
}
function playbackSpeed(){return sliderStop('speed',speedStops,11);}
function playerSpeed(){return sliderStop('player-speed',playerSpeedStops,5);}
function mouseSensitivity(){return .015*sliderStop('sensitivity',sensitivityStops,6);}
function rotateSpeed(){return sliderStop('rotate-speed',rotateSpeedStops,3);}
function multiplier(value){return `${Number(value.toFixed(2))}×`;}
function showError(error){$('status').textContent=error.message;$('status').classList.add('error');console.error(error);}
function installFlyer(bytes,title,origin=[0,0,0],preserveCamera=false) {
  const result=runEngine(bytes);
  motionFrameKey='';
  sourceBytes=result.bytes;sourceTitle=title;sourceOrigin=origin.map((value,i)=>value-result.shift[i]);
  history=[{tick:0,bytes:result.bytes,origin:sourceOrigin}];frontier=0;tickIndex=0;
  detailTrace=null;detailBase=0;stepIndex=0;trace=shiftTrace(result.trace,sourceOrigin);selected=null;
  travelOriginX=trace.initial.length?trace.initial.reduce((min,row)=>Math.min(min,row[0]),Infinity):0;
  editFlyer=parseFlyer(sourceBytes);
  if(sourceOrigin.some(Boolean)){
    const world=id=>id.split(',').map((value,i)=>Number(value)+sourceOrigin[i]).join(',');
    editFlyer.cells=new Map([...editFlyer.cells].map(([id,cell])=>[world(id),cell]));
    editFlyer.pistonLists=new Map([...editFlyer.pistonLists].map(([owner,members])=>[world(owner),members.map(world)]));
  }
  allBounds=computeBounds(trace);startBounds=allBounds;
  $('run-title').textContent=title;$('flyer-meta').textContent=`Push limit ${trace.push_limit} · ${trace.initial.length} blocks`;
  $('push-limit').value=String(trace.push_limit);
  $('status').textContent='';$('status').classList.remove('error');
  $('export').disabled=false;
  stopPlayback();if(!preserveCamera)frameCamera();render();followAnchor.copy(flyerMiddle);followVelocity.set(0,0,0);
}
const paletteSlots=[
  {slot:1,kind:9,sticky:false,label:'Piston'},
  {slot:2,kind:9,sticky:true,label:'Sticky piston'},
  {slot:3,kind:1,label:'Slime'},
  {slot:4,kind:2,label:'Honey'},
  {slot:5,kind:6,label:'Redstone block'},
  {slot:6,kind:7,label:'Observer'},
  {slot:7,kind:8,label:'Rod'},
  {slot:8,kind:5,label:'Glazed terracotta'},
  {slot:9,kind:3,label:'Smooth stone'},
  {slot:0,kind:4,label:'Glass'},
];
function drawPaletteIcon(canvas,entry){
  const ctx=canvas.getContext('2d');
  const face=(texture,origin,u,v,shade=0)=>{
    const end=[origin[0]+u[0]+v[0],origin[1]+u[1]+v[1]];
    ctx.save();ctx.beginPath();ctx.moveTo(...origin);ctx.lineTo(origin[0]+u[0],origin[1]+u[1]);
    ctx.lineTo(...end);ctx.lineTo(origin[0]+v[0],origin[1]+v[1]);ctx.closePath();ctx.clip();
    ctx.setTransform(u[0]/64,u[1]/64,v[0]/64,v[1]/64,origin[0],origin[1]);
    ctx.drawImage(texture.image,0,0,64,64);ctx.setTransform(1,0,0,1,0,0);
    if(shade){ctx.fillStyle=`rgba(0,17,22,${shade})`;ctx.fill();}ctx.restore();
  };
  if(entry.kind===8){
    ctx.fillStyle='#b7c7c7';ctx.fillRect(17,31,19,7);
    ctx.fillStyle='#f6faf3';ctx.fillRect(21,8,10,27);
    ctx.fillStyle='#c7d5d1';ctx.fillRect(28,11,4,24);
    ctx.fillStyle='#ffffff';ctx.fillRect(22,6,8,5);
    return;
  }
  const piston={sticky:!!entry.sticky,angry:false,state:0};
  const top=entry.kind===9?pistonTexture(2,piston,false):entry.kind===7?observerTexture(2,false):plainTexture(entry.kind);
  const left=entry.kind===9?pistonTexture('front',piston,false):entry.kind===7?observerTexture(5,false):plainTexture(entry.kind);
  const right=entry.kind===9?pistonTexture(0,piston,false):entry.kind===7?observerTexture(0,false):plainTexture(entry.kind);
  face(left,[4,12],[20,10],[0,22],.16);
  face(right,[24,22],[20,-10],[0,22],.06);
  face(top,[24,2],[20,10],[-20,10]);
  ctx.strokeStyle='#e4f9efaa';ctx.lineWidth=.8;
  ctx.beginPath();ctx.moveTo(4,12);ctx.lineTo(24,2);ctx.lineTo(44,12);ctx.lineTo(44,34);
  ctx.lineTo(24,44);ctx.lineTo(4,34);ctx.closePath();ctx.stroke();
}
for(const entry of paletteSlots){
  const button=document.createElement('button');button.type='button';button.className='edit-slot';button.title=`${entry.slot}: ${entry.label}`;
  button.dataset.slot=String(entry.slot);button.setAttribute('aria-label',`${entry.slot}: ${entry.label}`);
  const number=document.createElement('kbd');number.textContent=entry.slot;
  const icon=document.createElement('canvas');icon.className='block-icon';icon.width=48;icon.height=48;
  drawPaletteIcon(icon,entry);
  button.append(number,icon);button.onclick=()=>selectSlot(entry.slot);
  $('edit-hotbar').appendChild(button);
}
function selectSlot(slot){
  selectedSlot=slot;
  for(const button of $('edit-hotbar').children){
    const active=Number(button.dataset.slot)===slot;
    button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));
  }
  rememberFlyer();
}
selectSlot(1);
function setEditorMode(mode){
  if(editorMode===mode||!sourceBytes)return;
  stopPlayback();
  if(mode==='edit'){
    const previousX=flyerMiddle.x;
    installFlyer(sourceBytes,sourceTitle,sourceOrigin,true);
    if($('follow-flyer').checked)camera.position.x+=flyerMiddle.x-previousX;
    if(playbackMode!=='ticks')setMode('ticks');
  }
  editorMode=mode;
  selected=null;
  for(const choice of ['view','edit']){
    const active=choice===mode;
    $('mode-'+choice).classList.toggle('active',active);
    $('mode-'+choice).setAttribute('aria-pressed',String(active));
  }
  $('edit-hotbar').hidden=mode!=='edit';
  $('push-limit').disabled=mode!=='edit';
  if(mode==='edit')$('push-limit').removeAttribute('aria-description');
  else $('push-limit').setAttribute('aria-description','Enter Edit mode to change the push limit');
  $('inspector-section').hidden=mode==='edit';
  for(const id of ['reset','direction','step','play','speed','mode-ticks','mode-detailed'])$(id).disabled=mode==='edit';
  $('viewport').classList.toggle('editing',mode==='edit');
  editGesture=null;clearPlacementPreview();
  if(mode==='view')hoverOutline.visible=false;
  render();
  rememberFlyer();
}
function saveEditedFlyer(){
  const {bytes,shift}=serializeFlyer(editFlyer);
  installFlyer(bytes,sourceTitle,shift.map(value=>-value),true);
  rememberFlyer();
}
function editCell(pos,cell){
  if(!editFlyer)return;
  const id=key(pos),previous=new Map(editFlyer.cells),previousLists=new Map(editFlyer.pistonLists);
  try{
    if(cell===null){
      const owned=editFlyer.pistonLists.get(id)||[];
      for(const member of owned)if(editFlyer.cells.has(member))
        editFlyer.cells.set(member,editFlyer.cells.get(member)&~16);
      editFlyer.cells.delete(id);editFlyer.pistonLists.delete(id);
      for(const [owner,members] of editFlyer.pistonLists){
        const remaining=members.filter(member=>member!==id);
        if(remaining.length)editFlyer.pistonLists.set(owner,remaining);else editFlyer.pistonLists.delete(owner);
      }
    }else{
      if(editFlyer.cells.has(id)){
        $('status').textContent='That cell is occupied; left-click to remove its block first.';
        $('status').classList.remove('error');return;
      }
      editFlyer.cells.set(id,cell);
    }
    saveEditedFlyer();
  }catch(error){editFlyer.cells=previous;editFlyer.pistonLists=previousLists;showError(error);}
}
function commitPushLimit(){
  if(editorMode!=='edit'||!editFlyer)return;
  const old=editFlyer.pushLimit,value=Number($('push-limit').value);
  if(!Number.isSafeInteger(value)||value<0){
    $('push-limit').value=String(old);showError(Error('Push limit must be a nonnegative whole number.'));return;
  }
  try{
    editFlyer.pushLimit=value;saveEditedFlyer();
  }catch(error){editFlyer.pushLimit=old;$('push-limit').value=String(old);showError(error);}
}
$('push-limit').addEventListener('change',commitPushLimit);
$('push-limit').addEventListener('keydown',event=>{
  if(event.key==='Enter'){event.preventDefault();commitPushLimit();$('push-limit').blur();}
});
for(const tabName of ['general','debug'])$('tab-'+tabName).onclick=()=>{
  for(const name of ['general','debug']){
    const active=name===tabName;
    $('tab-'+name).classList.toggle('active',active);
    $('tab-'+name).setAttribute('aria-selected',String(active));
    $('panel-'+name).hidden=!active;
  }
};
$('export').onclick=()=>{
  if(!sourceBytes)return;
  const url=URL.createObjectURL(new Blob([sourceBytes],{type:'application/octet-stream'}));
  const link=document.createElement('a');link.href=url;
  link.download=(sourceTitle.replace(/\.flyer$/i,'').replace(/[\\/:*?"<>|]/g,'_')||'flyer')+'.flyer';
  document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
};
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
      rememberFlyer();
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
    const candidates=items.filter(item=>item.push_limit>=min&&item.push_limit<=max
      &&(!search||`${item.name} ${item.path}`.toLowerCase().includes(search))
      &&tags.every(tag=>item.categories?.includes(tag)));
    let filtered=candidates;
    if($('filter-frontier').checked){
      const byLimit=new Map();
      for(const item of candidates)if(Number.isFinite(item.speed_bps)){
        if(!byLimit.has(item.push_limit))byLimit.set(item.push_limit,[]);
        byLimit.get(item.push_limit).push(item);
      }
      const frontierItems=new Set();
      let previousBest=-Infinity,lastIncludedLimit=null;
      for(const limit of [...byLimit.keys()].sort((a,b)=>a-b)){
        const group=byLimit.get(limit),best=Math.max(...group.map(item=>item.speed_bps));
        const gain=best-previousBest;
        if(gain>.002+1e-9||(lastIncludedLimit!==null&&limit===lastIncludedLimit+1&&gain>1e-9)){
          for(const item of group)if(best-item.speed_bps<=.005+1e-9)frontierItems.add(item);
          lastIncludedLimit=limit;
        }
        previousBest=Math.max(previousBest,best);
      }
      filtered=candidates.filter(item=>frontierItems.has(item));
    }
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
  for(const id of ['bank-min','bank-max','bank-sort','filter-frontier',...filterTags.map(([id])=>id)])$(id).onchange=update;
  $('bank-search').oninput=update;
  $('bank-clear').onclick=()=>{resetRange();$('bank-search').value='';$('filter-frontier').checked=false;for(const [id] of filterTags)$(id).checked=false;update();};
  update();$('open-bank').disabled=false;
}
$('open-bank').disabled=true;
$('open-bank').onclick=()=>{setDisplayFocused(false);$('bank-dialog').showModal();};
$('close-bank').onclick=()=>$('bank-dialog').close();
$('open-help').onclick=()=>{setDisplayFocused(false);$('help-dialog').showModal();};
$('close-help').onclick=()=>$('help-dialog').close();
$('help-got-it').onclick=()=>$('help-dialog').close();
$('help-dialog').addEventListener('click',event=>{
  if(event.target!==$('help-dialog'))return;
  const rect=$('help-dialog').getBoundingClientRect();
  if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)$('help-dialog').close();
});
$('bank-dialog').addEventListener('click',event=>{
  if(event.target!==$('bank-dialog'))return;
  const rect=$('bank-dialog').getBoundingClientRect();
  if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)$('bank-dialog').close();
});
$('file').onchange=async event=>{const file=event.target.files[0];if(!file)return;try{installFlyer(new Uint8Array(await file.arrayBuffer()),file.name);rememberFlyer();}catch(error){showError(error);}};
$('reset').onclick=()=>{
  if(!sourceBytes||editorMode==='edit')return;
  const wasPlaying=playing,previousMiddle=flyerMiddle.clone();
  installFlyer(sourceBytes,sourceTitle,sourceOrigin,true);
  if($('follow-flyer').checked)camera.position.x+=flyerMiddle.x-previousMiddle.x;
  if(wasPlaying){playing=true;$('play').textContent='Ⅱ';$('play').setAttribute('aria-label','Pause');}
};
function setPlaybackDirection(value){
  direction=value;
  $('direction').textContent=direction>0?'→':'←';
  $('direction').setAttribute('aria-label',`Direction: ${direction>0?'forward':'backward'}`);
  $('step').textContent=direction>0?'›':'‹';
  $('step').setAttribute('aria-label',`Step ${direction>0?'forward':'backward'}`);
}
$('direction').onclick=()=>{if(editorMode==='view')setPlaybackDirection(-direction);};
$('step').onclick=()=>{if(editorMode==='view')advance(direction);};
$('speed').oninput=()=>{const label=`${playbackSpeed()}×`;$('speed-label').textContent=label;$('speed').setAttribute('aria-valuetext',label);};
$('player-speed').oninput=()=>{const label=multiplier(playerSpeed()/playerSpeedStops[5]);$('player-speed-label').textContent=label;$('player-speed').setAttribute('aria-valuetext',label);};
$('sensitivity').oninput=()=>{const label=multiplier(mouseSensitivity()/(.015*sensitivityStops[6]));$('sensitivity-label').textContent=label;$('sensitivity').setAttribute('aria-valuetext',label);};
$('rotate-speed').oninput=()=>{const label=multiplier(rotateSpeed());$('rotate-speed-label').textContent=label;$('rotate-speed').setAttribute('aria-valuetext',label);};
function resetSpeedControls(){
  for(const id of ['speed','player-speed','sensitivity','rotate-speed']){
    $(id).value='50';
    $(id).dispatchEvent(new Event('input'));
  }
}
resetSpeedControls();
window.addEventListener('pageshow',resetSpeedControls);
for(const mode of ['real','halfway','smooth'])$('moving-'+mode).onclick=()=>{
  movingDisplayMode=mode;motionFrameKey='';
  for(const choice of ['real','halfway','smooth']){
    const active=choice===mode;
    $('moving-'+choice).classList.toggle('active',active);
    $('moving-'+choice).setAttribute('aria-pressed',String(active));
  }
  render();
};
$('follow-flyer').onchange=()=>{followAnchor.copy(flyerMiddle);followVelocity.set(0,0,0);};
$('mode-ticks').onclick=()=>setMode('ticks');
$('mode-detailed').onclick=()=>setMode('detailed');
for(const choice of ['view','edit'])$('mode-'+choice).onclick=()=>setEditorMode(choice);
function togglePlayback(){
  if(!trace||editorMode==='edit')return;
  if(playing){stopPlayback();return;}
  playing=true;playbackAccumulator=0;
  $('play').textContent='Ⅱ';$('play').setAttribute('aria-label','Pause');
}
$('play').onclick=togglePlayback;
for(const id of ['show-power','show-move','show-owners','show-chunks','slice-x-on','slice-y-on','slice-z-on','slice-x','slice-y','slice-z'])$(id).addEventListener('input',render);
$('show-floor').addEventListener('change',()=>{if(ground)ground.visible=$('show-floor').checked;});
let drag=null;
let editGesture=null,lastPointer=null;
let recaptureButton=null;
const hoverOutline=new THREE.LineSegments(frontOutlineGeometry(1.045,7),
  new THREE.LineBasicMaterial({color:0x8ffff0,transparent:true,opacity:.98,depthTest:true,depthWrite:false}));
hoverOutline.visible=false;hoverOutline.renderOrder=10;scene.add(hoverOutline);
const placementPreview=new THREE.Group();placementPreview.renderOrder=12;scene.add(placementPreview);
const previewMaterials=new Map();
const EDIT_REACH=36;
let previewSignature='';
function previewMaterial(texture){
  if(!previewMaterials.has(texture.uuid))previewMaterials.set(texture.uuid,
    new THREE.MeshBasicMaterial({map:texture,transparent:true,opacity:.45,depthWrite:false,side:THREE.FrontSide}));
  return previewMaterials.get(texture.uuid);
}
function clearPlacementPreview(){
  placementPreview.traverse(object=>{if(object.isInstancedMesh)object.dispose();});
  placementPreview.clear();previewSignature='';
}
function showPlacementPreview(positions,cell,ghost=false){
  const signature=`${cell}:${ghost}:${positions.map(key).join('|')}`;
  if(signature===previewSignature)return;
  clearPlacementPreview();previewSignature=signature;
  if(!positions.length)return;
  const block=decode(cell);
  if(block.kind===8){
    const pos=positions[0],rod=new THREE.Group();rod.position.copy(point(pos));
    rod.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),point(directions[block.direction]));
    const shaft=standardMaterial(faceTexture('rod-shaft'),.76);
    const base=standardMaterial(faceTexture('rod-base'),.7);
    for(const [size,y,material] of [[[.42,.18,.42],-.36,base],[[.22,.66,.22],.02,shaft],[[.3,.12,.3],.39,shaft]]){
      const mesh=new THREE.Mesh(box(...size),material);mesh.position.y=y;rod.add(mesh);
    }
    placementPreview.add(rod);return;
  }
  if(block.kind===7||block.kind===9){
    const maps=Array.from({length:6},(_,index)=>block.kind===7?observerTexture(index,false):
      pistonTexture(index===4?'front':index===5?'back':index,block,false));
    const mesh=new THREE.Mesh(box(),maps.map(texture=>standardMaterial(texture,.84)));
    mesh.position.copy(point(positions[0]));orientBlock(mesh,block.direction);
    placementPreview.add(mesh);return;
  }
  const texture=plainTexture(block.kind);
  const solidMaterial=standardMaterial(texture,.73,{metalness:.03,transparent:block.kind===4,
    opacity:block.kind===4?.42:1,depthWrite:block.kind!==4});
  const append=(cells,material,shape)=>{
    if(!cells.length)return;
    const mesh=new THREE.InstancedMesh(shape,material,cells.length),dummy=new THREE.Object3D();
    cells.forEach((pos,index)=>{dummy.position.copy(point(pos));dummy.updateMatrix();mesh.setMatrixAt(index,dummy.matrix);});
    mesh.instanceMatrix.needsUpdate=true;placementPreview.add(mesh);
  };
  append(ghost?positions.slice(0,1):positions,solidMaterial,box());
  if(ghost)append(positions.slice(1),previewMaterial(texture),box(.96,.96,.96));
}
function aimRayAt(event){
  const rect=renderer.domElement.getBoundingClientRect();
  const locked=document.pointerLockElement===renderer.domElement;
  const x=locked?rect.left+rect.width/2:event.clientX,y=locked?rect.top+rect.height/2:event.clientY;
  pointer.x=((x-rect.left)/rect.width)*2-1;pointer.y=-((y-rect.top)/rect.height)*2+1;
  raycaster.setFromCamera(pointer,camera);
  return raycaster.ray;
}
function hitAt(event,reach=Infinity){
  aimRayAt(event);
  const hit=raycaster.intersectObjects(pickables)[0];
  if(!hit||hit.distance>reach)return null;
  const pos=hit.object.userData.pos||hit.object.userData.positions?.[hit.instanceId];
  return pos?{hit,pos}:null;
}
function hoverAt(event){
  if(editorMode!=='edit')return;
  const target=hitAt(event,EDIT_REACH);hoverOutline.visible=!!target;
  if(target){
    hoverOutline.position.copy(point(target.pos));
    hoverOutline.geometry=frontOutlineGeometry(1.045,outlineOctant(target.pos));
  }
}
function faceDirection(hit){
  const normal=hit.face?.normal?.clone().transformDirection(hit.object.matrixWorld);
  if(!normal)return 0;
  let best=0,score=-Infinity;
  directions.forEach((vector,index)=>{const dot=normal.dot(point(vector));if(dot>score){score=dot;best=index;}});
  return best;
}
function dominantDirection(vector){
  let axis=0;
  for(let i=1;i<3;i++)if(Math.abs(vector.getComponent(i))>Math.abs(vector.getComponent(axis)))axis=i;
  return axis*2+(vector.getComponent(axis)<0?1:0);
}
function movementKeyDirection(moveKey){
  if(moveKey==='space')return 2;
  if(moveKey==='shift')return 3;
  const forward=new THREE.Vector3();camera.getWorldDirection(forward);forward.y=0;
  if(forward.lengthSq()<.0001)forward.set(0,0,-1);
  forward.normalize();
  const right=new THREE.Vector3().crossVectors(forward,new THREE.Vector3(0,1,0)).normalize();
  return dominantDirection(moveKey==='w'?forward:moveKey==='s'?forward.negate():moveKey==='d'?right:right.negate());
}
function placementCell(entry,facing){
  return entry.kind|(entry.sticky?256:0)|([7,8,9].includes(entry.kind)?facing<<5:0);
}
function emptyRowExtent(gesture,event){
  if(!event)return 0;
  const ray=aimRayAt(event),fromEye=gesture.start.map((value,i)=>value-ray.origin.getComponent(i));
  const parallel=ray.direction.getComponent(gesture.axis)*gesture.axisSign;
  const along=fromEye[gesture.axis]*gesture.axisSign;
  const towardEye=fromEye.reduce((sum,value,i)=>sum+value*ray.direction.getComponent(i),0);
  const eyeDistanceSq=fromEye.reduce((sum,value)=>sum+value*value,0);
  const denominator=1-parallel*parallel;
  const closest=denominator<.0001?EDIT_REACH:
    (towardEye-parallel*along)/denominator;
  if(closest<0)return 0;
  const rayDistance=Math.min(EDIT_REACH,closest);
  const aimedExtent=parallel*rayDistance-along;
  // The player can walk during a hold. Cap the endpoint from their current
  // position, rather than limiting the entire row to its original position.
  const discriminant=along*along+EDIT_REACH*EDIT_REACH-eyeDistanceSq;
  if(discriminant<0)return 0;
  const reachableExtent=-along+Math.sqrt(discriminant);
  return Math.max(0,Math.min(Math.round(aimedExtent),Math.floor(reachableExtent+1e-6)));
}
function placementPlan(gesture){
  const entry=gesture.entry,start=gesture.start;
  if(!entry||!start||!editFlyer)return {positions:[],cell:0};
  let facing=entry.kind===9?(entry.sticky?1:0):gesture.face^1;
  if([7,8,9].includes(entry.kind)){
    if(gesture.lastMoveDirection!==null)
      facing=entry.kind===8?gesture.lastMoveDirection^1:gesture.lastMoveDirection;
  }
  const cell=placementCell(entry,facing),positions=[];
  if(editFlyer.cells.has(key(start)))return {positions,cell};
  positions.push(start);
  if([7,8,9].includes(entry.kind)||!gesture.rowPlace)return {positions,cell};
  if(gesture.axis===null)return {positions,cell};
  const extent=emptyRowExtent(gesture,lastPointer);
  for(let step=1;step<=extent;step++){
    const pos=[...start];pos[gesture.axis]+=step*gesture.axisSign;
    if(editFlyer.cells.has(key(pos)))break;
    positions.push(pos);
  }
  return {positions,cell};
}
function updatePlacementPreview(){
  if(!editGesture?.previewPlace)return;
  const plan=placementPlan(editGesture);
  showPlacementPreview(plan.positions,plan.cell,editGesture.rowPlace&&editGesture.axis!==null);
}
function placePlannedBlocks(plan){
  if(!editFlyer||!plan.positions.length)return;
  const before=new Map(editFlyer.cells);
  try{
    let placed=0;
    for(const pos of plan.positions){
      const id=key(pos);if(editFlyer.cells.has(id))break;
      editFlyer.cells.set(id,plan.cell);placed++;
    }
    if(placed)saveEditedFlyer();
  }catch(error){editFlyer.cells=before;showError(error);}
}
function pickBlockAtAim(event=lastPointer){
  if(!event||editorMode!=='edit')return;
  const target=hitAt(event,EDIT_REACH);if(!target)return;
  const cell=editFlyer?.cells.get(key(target.pos));
  if(cell!==undefined){
    const slot=paletteSlots.find(entry=>entry.kind===(cell&15)&&(entry.kind!==9||entry.sticky===!!(cell&256)));
    if(slot)selectSlot(slot.slot);
  }
}
function cycleStateAtAim(event=lastPointer){
  if(!event||editorMode!=='edit'||!editFlyer)return;
  const target=hitAt(event,EDIT_REACH);if(!target)return;
  const id=key(target.pos),cell=editFlyer.cells.get(id);
  if(cell===undefined)return;
  const block=decode(cell);
  if(block.kind===7){
    editFlyer.cells.set(id,cell^256);
    try{saveEditedFlyer();}catch(error){editFlyer.cells.set(id,cell);showError(error);}
    return;
  }
  if(block.kind!==9)return;
  const nextState=(block.state+1)%4;
  const front=target.pos.map((value,i)=>value+directions[block.direction][i]);
  const frontId=key(front),frontCell=editFlyer.cells.get(frontId);
  if(block.state===0&&frontCell!==undefined){
    $('status').textContent='Cannot extend: the cell in front is occupied.';
    $('status').classList.remove('error');return;
  }
  editFlyer.cells.set(id,(cell&~(3<<10))|(nextState<<10));
  if(block.state===0)editFlyer.cells.set(frontId,10);
  const ownArm=(trace.initial_arms||[]).some(([pos,facing])=>key(pos)===frontId&&facing===block.direction);
  if(block.state===2&&frontCell!==undefined&&(frontCell&15)===10&&ownArm)editFlyer.cells.delete(frontId);
  try{saveEditedFlyer();}
  catch(error){
    editFlyer.cells.set(id,cell);
    if(frontCell===undefined)editFlyer.cells.delete(frontId);else editFlyer.cells.set(frontId,frontCell);
    showError(error);
  }
}
let displayFocused=false;
const heldKeys=new Set();
const movementKeys=['w','a','s','d','space','shift'];
let sprintMultiplier=1,lastWPress=-Infinity;
function setSprintMultiplier(value){
  sprintMultiplier=value;
  $('sprint-indicator').hidden=value<=1;
  $('sprint-indicator').textContent=`SPRINTING · ${multiplier(value)}`;
}
function setDisplayFocused(value){
  displayFocused=value;renderer.domElement.classList.toggle('display-focused',value);
  if(!value){heldKeys.clear();cameraVelocity.set(0,0,0);setSprintMultiplier(1);lastWPress=-Infinity;}
}
function breakAtAim(event){
  if(!editGesture?.fullscreenBreak)return;
  const now=performance.now();
  if(!editGesture.aimMoved&&now-editGesture.lastBreakAt<155)return;
  const target=hitAt(event,EDIT_REACH);if(!target)return;
  const id=key(target.pos);
  if(!editFlyer?.cells.has(id))return;
  editGesture.lastBreakAt=now;
  editGesture.aimMoved=false;
  editCell(target.pos,null);
}
renderer.domElement.addEventListener('pointerdown',event=>{
  if(![0,1,2].includes(event.button))return;
  setDisplayFocused(true);
  renderer.domElement.focus();
  lastPointer={clientX:event.clientX,clientY:event.clientY};
  if(document.fullscreenElement===$('viewport')&&document.pointerLockElement!==renderer.domElement){
    // This press is only for recapturing the pointer. Never edit or turn the
    // camera until its matching release, even if capture succeeds mid-press.
    editGesture=null;drag=null;clearPlacementPreview();
    recaptureButton=event.button;
    capturePointer().catch(()=>{});
    event.preventDefault();return;
  }
  if(editorMode==='edit'){
    if(event.button===1){event.preventDefault();pickBlockAtAim(event);return;}
    const aimed=hitAt(event),target=aimed?.hit.distance>EDIT_REACH?null:aimed;
    if(aimed&&!target){$('status').textContent=`Placement requires a block within ${EDIT_REACH} blocks of the player.`;$('status').classList.remove('error');}
    const face=target?faceDirection(target.hit):0;
    editGesture={button:event.button,startX:event.clientX,startY:event.clientY,
      dx:0,dy:0,target,face,
      fullscreenBreak:event.button===0&&document.fullscreenElement===$('viewport'),
      previewPlace:event.button===2,rowPlace:event.button===2,
      entry:paletteSlots.find(item=>item.slot===selectedSlot),
      start:target?target.pos.map((value,i)=>value+directions[face][i]):null,
      lastMoveDirection:null,axis:null,axisSign:0,
      lastBreakAt:-Infinity,aimMoved:true};
    if(editGesture.fullscreenBreak)breakAtAim(event);
    if(editGesture.previewPlace)updatePlacementPreview();
    if(document.fullscreenElement!==$('viewport'))
      drag={x:event.clientX,y:event.clientY,startX:event.clientX,startY:event.clientY};
    if(document.fullscreenElement!==$('viewport'))renderer.domElement.setPointerCapture(event.pointerId);
    event.preventDefault();return;
  }
  if(event.button!==0)return;
  if(document.fullscreenElement===$('viewport'))return;
  drag={x:event.clientX,y:event.clientY,startX:event.clientX,startY:event.clientY};
  renderer.domElement.setPointerCapture(event.pointerId);
});
renderer.domElement.addEventListener('pointermove',event=>{
  lastPointer={clientX:event.clientX,clientY:event.clientY};
  if(recaptureButton!==null)return;
  const locked=document.pointerLockElement===renderer.domElement;
  if(editorMode==='edit'){
    hoverAt(event);
    if(editGesture){
      editGesture.dx=locked?editGesture.dx+event.movementX:event.clientX-editGesture.startX;
      editGesture.dy=locked?editGesture.dy+event.movementY:event.clientY-editGesture.startY;
    }
  }
  if(!locked&&!drag){
    if(editGesture?.fullscreenBreak&&(event.buttons&1)){
      editGesture.aimMoved=Math.abs(event.movementX)+Math.abs(event.movementY)>1;
      breakAtAim(event);
    }
    return;
  }
  const dx=locked?event.movementX:event.clientX-drag.x;
  const dy=locked?event.movementY:event.clientY-drag.y;
  if(!locked){drag.x=event.clientX;drag.y=event.clientY;}
  // Rotate the player's view in place. The camera position never changes.
  camera.rotation.y-=dx*mouseSensitivity();
  camera.rotation.x=Math.max(-Math.PI/2+.02,Math.min(Math.PI/2-.02,camera.rotation.x-dy*mouseSensitivity()));
  if(editGesture?.fullscreenBreak&&(event.buttons&1)){
    editGesture.aimMoved=Math.abs(dx)+Math.abs(dy)>1;
    breakAtAim(event);
  }
});
renderer.domElement.addEventListener('pointerup',event=>{
  if(recaptureButton===event.button){recaptureButton=null;event.preventDefault();return;}
  if(editorMode==='edit'){
    if(!editGesture||editGesture.button!==event.button)return;
    const {button,target,dx,dy,fullscreenBreak}=editGesture;
    const plan=button===2?placementPlan(editGesture):null;
    editGesture=null;drag=null;clearPlacementPreview();
    if(button===2){placePlannedBlocks(plan);return;}
    if(!target)return;
    if(button===0){if(!fullscreenBreak&&Math.hypot(dx,dy)<=5)editCell(target.pos,null);return;}
    return;
  }
  if(document.fullscreenElement===$('viewport'))return;
  if(!drag)return;
  const wasClick=Math.abs(event.clientX-drag.startX)<=4&&Math.abs(event.clientY-drag.startY)<=4;
  drag=null;
  if(!wasClick)return;
  const rect=renderer.domElement.getBoundingClientRect();pointer.x=((event.clientX-rect.left)/rect.width)*2-1;pointer.y=-((event.clientY-rect.top)/rect.height)*2+1;
  raycaster.setFromCamera(pointer,camera);const hit=raycaster.intersectObjects(pickables)[0];selected=hit?(hit.object.userData.pos||hit.object.userData.positions?.[hit.instanceId]||null):null;render();
});
renderer.domElement.addEventListener('pointercancel',()=>{drag=null;editGesture=null;recaptureButton=null;clearPlacementPreview();});
window.addEventListener('pointerup',event=>{if(recaptureButton===event.button)recaptureButton=null;});
renderer.domElement.addEventListener('pointerleave',()=>{if(document.pointerLockElement!==renderer.domElement)hoverOutline.visible=false;});
renderer.domElement.addEventListener('contextmenu',event=>event.preventDefault());
async function capturePointer(){
  await renderer.domElement.requestPointerLock();
  if(document.pointerLockElement!==renderer.domElement)throw Error('Mouse capture was not granted.');
  $('status').textContent='';$('status').classList.remove('error');
}
async function toggleFullscreen(){
  if(document.fullscreenElement===$('viewport')){await document.exitFullscreen();return;}
  try{
    await $('viewport').requestFullscreen();
    try{await capturePointer();}catch{/* A later canvas click can retry pointer lock. */}
  }catch(error){
    showError(Error(`Could not enter fullscreen: ${error.message}`));
  }
}
$('fullscreen').onclick=toggleFullscreen;
document.addEventListener('fullscreenchange',()=>{
  const active=document.fullscreenElement===$('viewport');
  $('fullscreen').setAttribute('aria-label',active?'Exit fullscreen':'Enter fullscreen');
  if(active){
    setDisplayFocused(true);renderer.domElement.focus({preventScroll:true});
  }
  else{
    recaptureButton=null;
    editGesture=null;clearPlacementPreview();
    if(document.pointerLockElement===renderer.domElement)document.exitPointerLock();
    setDisplayFocused(false);
  }
  resize();
});
document.addEventListener('pointerlockchange',()=>{
  const locked=document.pointerLockElement===renderer.domElement;
  $('viewport').classList.toggle('pointer-locked',locked);
  if(locked){
    setDisplayFocused(true);renderer.domElement.focus({preventScroll:true});
  }
});
renderer.domElement.addEventListener('wheel',event=>{
  if(!displayFocused)return;
  event.preventDefault();
  const forward=new THREE.Vector3();camera.getWorldDirection(forward);
  const distance=camera.position.distanceTo(flyerMiddle);
  const step=Math.max(.8,distance*.08);
  camera.position.addScaledVector(forward,-Math.sign(event.deltaY)*step);
},{passive:false});
const playbackControls=new Set(['reset','direction','step','play','speed','player-speed','sensitivity','follow-flyer','mode-ticks','mode-detailed','mode-view','mode-edit']);
document.addEventListener('pointerdown',event=>{
  if(event.target===renderer.domElement||playbackControls.has(event.target.id)||event.target.closest('.navigation-panel, .edit-hotbar'))return;
  setDisplayFocused(false);renderer.domElement.blur();
},true);
window.addEventListener('keydown',event=>{
  if(event.key==='Escape'&&document.fullscreenElement===$('viewport')){
    event.preventDefault();document.exitFullscreen();return;
  }
  if($('bank-dialog').open||$('help-dialog').open)return;
  if(event.target instanceof HTMLElement&&(event.target.matches('input, textarea, select')||event.target.isContentEditable))return;
  if(event.key==='Enter'&&displayFocused){event.preventDefault();if(!event.repeat)toggleFullscreen();return;}
  if(event.key.toLowerCase()==='x'){event.preventDefault();if(!event.repeat){
    if(editorMode==='edit'){setEditorMode('view');togglePlayback();}else setEditorMode('edit');
  }return;}
  if(editorMode==='edit'&&/^[0-9]$/.test(event.key)){event.preventDefault();selectSlot(Number(event.key));return;}
  if(editorMode==='edit'&&event.key.toLowerCase()==='z'){event.preventDefault();pickBlockAtAim();return;}
  if(editorMode==='edit'&&event.key.toLowerCase()==='t'){event.preventDefault();if(!event.repeat)cycleStateAtAim();return;}
  if(event.key==='ArrowRight'){event.preventDefault();advance(1);return;}
  if(event.key==='ArrowLeft'){event.preventDefault();advance(-1);return;}
  const keyName=event.key.toLowerCase();
  if(keyName==='k'){event.preventDefault();if(!event.repeat)togglePlayback();return;}
  if(keyName==='j'||keyName==='l'){
    event.preventDefault();if(editorMode==='edit')return;
    const stepDirection=keyName==='j'?-1:1;
    setPlaybackDirection(stepDirection);advance(stepDirection);return;
  }
  const moveKey=event.code==='Space'?'space':event.code==='ShiftLeft'||event.code==='ShiftRight'?'shift':keyName;
  if(displayFocused&&moveKey==='f'){
    if(!event.repeat)setSprintMultiplier(Math.min(16,sprintMultiplier*2));
    event.preventDefault();return;
  }
  if(displayFocused&&[...movementKeys,'q','e'].includes(moveKey)){
    if(moveKey==='w'&&!event.repeat&&!heldKeys.has('w')){
      const now=performance.now();
      if(now-lastWPress<=300)setSprintMultiplier(Math.max(2,sprintMultiplier));
      lastWPress=now;
    }
    if(editGesture?.button===2&&movementKeys.includes(moveKey)&&!event.repeat&&!heldKeys.has(moveKey)){
      const latest=movementKeyDirection(moveKey);
      editGesture.lastMoveDirection=latest;
      if(editGesture.rowPlace&&editGesture.axis===null){
        editGesture.axis=Math.floor(latest/2);
        editGesture.axisSign=latest%2?-1:1;
      }
    }
    heldKeys.add(moveKey);
    event.preventDefault();
  }
});
window.addEventListener('keyup',event=>{
  const released=event.code==='Space'?'space':event.code==='ShiftLeft'||event.code==='ShiftRight'?'shift':event.key.toLowerCase();
  heldKeys.delete(released);
  if(movementKeys.includes(released)&&!movementKeys.some(key=>heldKeys.has(key))){cameraVelocity.set(0,0,0);setSprintMultiplier(1);}
});
window.addEventListener('blur',()=>{
  heldKeys.clear();cameraVelocity.set(0,0,0);setSprintMultiplier(1);lastWPress=-Infinity;
  drag=null;editGesture=null;recaptureButton=null;
  clearPlacementPreview();
});
const cameraVelocity=new THREE.Vector3();
function moveCamera(deltaSeconds) {
  if(!movementKeys.some(key=>heldKeys.has(key))){cameraVelocity.set(0,0,0);return;}
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
  if(heldKeys.has('space'))move.y+=1;
  if(heldKeys.has('shift'))move.y-=1;
  if(move.lengthSq()>0)move.normalize().multiplyScalar(
    BASE_PLAYER_BLOCKS_PER_SECOND*(playerSpeed()/playerSpeedStops[5])*sprintMultiplier);
  cameraVelocity.lerp(move,1-Math.exp(-dt/(move.lengthSq()>.0001?.12:.018)));
  if(cameraVelocity.lengthSq()<.00001)return;
  camera.position.addScaledVector(cameraVelocity,dt);
}
function followCamera(deltaSeconds){
  if(editorMode==='edit'||!$('follow-flyer').checked)return;
  const previous=followAnchor.clone();
  const dt=Math.min(deltaSeconds,.1),timeConstant=Math.max(.18,.65/Math.sqrt(playbackSpeed()));
  const omega=2/timeConstant,displacement=followAnchor.clone().sub(flyerMiddle);
  const velocityTerm=followVelocity.clone().addScaledVector(displacement,omega).multiplyScalar(dt);
  const decay=Math.exp(-omega*dt);
  followAnchor.copy(flyerMiddle).add(displacement.add(velocityTerm).multiplyScalar(decay));
  followVelocity.sub(velocityTerm.multiplyScalar(omega)).multiplyScalar(decay);
  camera.position.x+=followAnchor.x-previous.x;
}
const orbitAxis=new THREE.Vector3(0,1,0),orbitQuaternion=new THREE.Quaternion();
function orbitCamera(deltaSeconds){
  const turn=Number(heldKeys.has('q'))-Number(heldKeys.has('e'));
  if(!displayFocused||!turn||!trace)return;
  const angle=-turn*deltaSeconds*1.3*rotateSpeed();
  const offset=camera.position.clone().sub(flyerMiddle);
  orbitQuaternion.setFromAxisAngle(orbitAxis,angle);
  camera.position.copy(flyerMiddle).add(offset.applyQuaternion(orbitQuaternion));
  camera.quaternion.premultiply(orbitQuaternion);
}
function resize(){const el=$('canvas');renderer.setSize(el.clientWidth,el.clientHeight);camera.aspect=el.clientWidth/el.clientHeight;camera.updateProjectionMatrix();}
new ResizeObserver(resize).observe($('canvas'));resize();
let lastFrame=performance.now();
let lastHoverCheck=0;
function updateFrontOutlines(){
  for(const item of frontFacingOutlines){
    const octant=outlineOctant(item.pos);
    if(octant!==item.octant){item.lines.geometry=frontOutlineGeometry(item.size,octant);item.octant=octant;}
  }
  if(hoverOutline.visible){
    const pos=hoverOutline.position.toArray();
    hoverOutline.geometry=frontOutlineGeometry(1.045,outlineOctant(pos));
  }
}
function animate(now){
  requestAnimationFrame(animate);
  const dt=Math.min((now-lastFrame)/1000,.1);lastFrame=now;
  if(playing&&trace&&!$('bank-dialog').open&&!$('help-dialog').open){
    playbackAccumulator+=dt*10*playbackSpeed();
    let count=Math.min(Math.floor(playbackAccumulator),100);
    if(count){
      playbackAccumulator-=count;
      let changed=false;
      while(count--){if(!advance(direction,false)){stopPlayback();break;}changed=true;}
      if(changed){if(playbackMode==='ticks')showBoundary(tickIndex);else render();}
    }
  }
  followCamera(dt);
  orbitCamera(dt);
  moveCamera(dt);
  updatePlacementPreview();
  const desiredFov=47+(heldKeys.has('w')&&!heldKeys.has('s')?Math.min(13,2.6*Math.log2(sprintMultiplier)):0);
  const nextFov=camera.fov+(desiredFov-camera.fov)*(1-Math.exp(-dt/.16));
  if(Math.abs(nextFov-camera.fov)>.001){camera.fov=nextFov;camera.updateProjectionMatrix();}
  updateMovingVisuals(now);
  updatePistonHeads(now);
  updateMovingFlash(now);
  if(editorMode==='edit'&&document.pointerLockElement===renderer.domElement&&now-lastHoverCheck>70){
    hoverAt({clientX:0,clientY:0});lastHoverCheck=now;
  }
  if(editGesture?.fullscreenBreak)breakAtAim(lastPointer);
  updateFrontOutlines();
  sky.position.copy(camera.position);
  if(ground){ground.position.x=camera.position.x;ground.position.z=camera.position.z;}
  renderer.render(scene,camera);
}
requestAnimationFrame(animate);
async function initialize(){
  try{
    await loadWasm();
    const bank=loadBank().then(()=>null,error=>error);
    let restored=false;
    try{
      const saved=await readRecentFlyer();
      if(saved){
        restoringRecent=true;
        try{
          if(!(saved.bytes instanceof Uint8Array)||typeof saved.title!=='string'||
             !Array.isArray(saved.origin)||saved.origin.length!==3||
             !saved.origin.every(Number.isSafeInteger))throw Error('Invalid cached flyer');
          installFlyer(saved.bytes,saved.title,saved.origin);
          if(saved.mode==='edit')setEditorMode('edit');
          if(Number.isInteger(saved.slot)&&saved.slot>=0&&saved.slot<=9)selectSlot(saved.slot);
          $('status').textContent='Restored your last flyer from this browser.';
          restored=true;
        }finally{restoringRecent=false;}
      }
    }catch(error){console.warn('Could not restore the recent flyer',error);}
    if(!restored)await loadUrl('./demo.flyer','Six-block flyer');
    const bankError=await bank;
    if(bankError)throw bankError;
  }
  catch(error){showError(error);}
}
initialize();
