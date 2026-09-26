import * as THREE from 'three';

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
    // The simple wood-and-slime band always sits at the front edge.
    fill('#ac7e4e',5,5,13,54);
    fill(block.sticky?'#79d587':'#d7b37b',5,5,7,54);
    fill('#53615a',18,28,40,7);
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
  return [0,1,2,3,4,5].map(index=>new THREE.MeshStandardMaterial({
    map:displayedTexture(observer?observerTexture(index,block.powered)
      :pistonTexture(index===4?'front':index===5?'back':index,block,powered),block.moving),
    roughness:.84,
  }));
}

let trace = null, stepIndex = 0, tickIndex = 0, tickEnds = [0], playbackMode = 'ticks';
let selected = null, playing = null, loadedBytes = null;
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
const ambient = new THREE.AmbientLight(0xffffff,2.2); scene.add(ambient);
const light = new THREE.DirectionalLight(0xffffff,2.2); light.position.set(-5,12,8); scene.add(light);
const content = new THREE.Group(); scene.add(content);
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
let pickables = [];

function clearContent() {
  while (content.children.length) {
    const object=content.children[0]; content.remove(object);
    object.traverse(o=>{if(o.geometry)o.geometry.dispose(); if(o.material){const materials=Array.isArray(o.material)?o.material:[o.material];materials.forEach(m=>m.dispose());}});
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
  const edge=new THREE.EdgesGeometry(new THREE.BoxGeometry(size,size,size));
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
  return [0,1,2,3,4,5].map(index=>new THREE.MeshStandardMaterial({
    map:displayedTexture(index===0?headTexture(sticky):faceTexture('arm'),moving),roughness:.84,
  }));
}
function makeArm(pos,block,direction,sticky=false) {
  const movingHighlight=playbackMode==='detailed'&&block.moving;
  if(direction===undefined) {
    const mesh=pickable(new THREE.Mesh(new THREE.BoxGeometry(.78,.78,.78),
      new THREE.MeshStandardMaterial({map:displayedTexture(faceTexture('arm'),block.moving),roughness:.84})),pos);
    mesh.position.copy(point(pos));content.add(mesh);
    return;
  }
  const group=new THREE.Group();group.position.copy(point(pos));
  group.quaternion.setFromUnitVectors(new THREE.Vector3(1,0,0),point(directions[direction]));
  const wood=new THREE.MeshStandardMaterial({map:displayedTexture(faceTexture('arm'),block.moving),roughness:.84});
  const metalColor=new THREE.Color(0x77827f);
  if(block.moving)metalColor.lerp(new THREE.Color(0xffffff),.5);
  const metal=new THREE.MeshStandardMaterial({color:metalColor,roughness:.75});
  const shaft=pickable(new THREE.Mesh(new THREE.BoxGeometry(.72,.25,.25),wood),pos);group.add(shaft);
  const plate=pickable(new THREE.Mesh(new THREE.BoxGeometry(.17,1,1),headMaterials(sticky,block.moving)),pos);
  plate.position.x=.33;group.add(plate);
  const collar=pickable(new THREE.Mesh(new THREE.BoxGeometry(.13,.43,.43),metal),pos);
  collar.position.x=-.32;group.add(collar);
  content.add(group);
  if(movingHighlight)boxOutline(pos,0x7be4f4,1.02,.85);
}
function makeHalfwayHead(pos,block) {
  const group=new THREE.Group();group.position.copy(point(pos));
  group.quaternion.setFromUnitVectors(new THREE.Vector3(1,0,0),point(directions[block.direction]));
  const wood=new THREE.MeshStandardMaterial({map:displayedTexture(faceTexture('arm'),block.moving),roughness:.84});
  const shaft=pickable(new THREE.Mesh(new THREE.BoxGeometry(.52,.24,.24),wood),pos);
  shaft.position.x=.57;group.add(shaft);
  const plate=pickable(new THREE.Mesh(new THREE.BoxGeometry(.18,1,1),headMaterials(block.sticky,block.moving)),pos);
  plate.position.x=.91;group.add(plate);
  content.add(group);
}
function makeRod(pos,block) {
  const movingHighlight=playbackMode==='detailed'&&block.moving;
  const group=new THREE.Group();group.position.copy(point(pos));
  group.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),point(directions[block.direction]));
  const brass=new THREE.MeshStandardMaterial({map:displayedTexture(faceTexture('rod-shaft'),block.moving),metalness:.45,roughness:.38});
  const dark=new THREE.MeshStandardMaterial({map:displayedTexture(faceTexture('rod-base'),block.moving),metalness:.25,roughness:.55});
  const base=pickable(new THREE.Mesh(new THREE.BoxGeometry(.55,.19,.55),dark),pos);base.position.y=-.34;group.add(base);
  const shaft=pickable(new THREE.Mesh(new THREE.CylinderGeometry(.095,.12,.64,8),brass),pos);shaft.position.y=.02;group.add(shaft);
  const tip=pickable(new THREE.Mesh(new THREE.CylinderGeometry(.16,.12,.16,8),brass),pos);tip.position.y=.38;group.add(tip);
  content.add(group);
  if(movingHighlight)boxOutline(pos,0x7be4f4,1.02,.85);
}
function makeBlock(pos,cell,arms,armStickiness,powered=false) {
  const block=decode(cell);
  if(block.kind===10) {makeArm(pos,block,arms.get(key(pos)),armStickiness.get(key(pos))||false);return;}
  if(block.kind===8) {makeRod(pos,block);return;}
  const material=[7,9].includes(block.kind)?faceMaterials(block,powered&&!block.moving):new THREE.MeshStandardMaterial({map:displayedTexture(plainTexture(block.kind),block.moving),roughness:.73,metalness:.03,transparent:block.kind===4,opacity:block.kind===4?.48:1});
  const mesh=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),material);
  if([7,9].includes(block.kind))orientBlock(mesh,block.direction);
  mesh.position.copy(point(pos));content.add(mesh);pickable(mesh,pos);
  const movingHighlight=playbackMode==='detailed'&&block.moving;
  const outline=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002,1.002,1.002)),new THREE.LineBasicMaterial({color:movingHighlight?0x7be4f4:0x19242a,transparent:true,opacity:movingHighlight?1:.45}));
  outline.position.copy(mesh.position);content.add(outline);
}
function makeBulkBlocks(entries) {
  if(!entries.length)return;
  const groups=new Map();
  for(const [pos,cell] of entries) {
    const block=decode(cell), id=`${block.kind}-${block.moving}`;
    if(!groups.has(id))groups.set(id,[]);
    groups.get(id).push([pos,block]);
  }
  const geometry=new THREE.BoxGeometry(1,1,1),dummy=new THREE.Object3D();
  for(const group of groups.values()) {
    const block=group[0][1];
    const movingHighlight=playbackMode==='detailed'&&block.moving;
    const material=new THREE.MeshStandardMaterial({map:displayedTexture(plainTexture(block.kind),block.moving),roughness:.73,transparent:block.kind===4,opacity:block.kind===4?.48:1});
    const mesh=new THREE.InstancedMesh(geometry,material,group.length);
    mesh.userData.positions=group.map(([pos])=>pos);
    group.forEach(([pos],i)=>{dummy.position.copy(point(pos));dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);});
    mesh.instanceMatrix.needsUpdate=true;content.add(mesh);pickables.push(mesh);
  }
}
function addGround() {
  const min=allBounds.min,max=allBounds.max;
  const width=Math.max(max[0]-min[0]+2,max[2]-min[2]+2,10);
  const grid=new THREE.GridHelper(Math.ceil(width/2)*2,Math.ceil(width/2)*2,0x385056,0x26383e);
  grid.position.set((min[0]+max[0])/2,min[1]-.55,(min[2]+max[2])/2);
  grid.material.transparent=true;grid.material.opacity=playbackMode==='detailed'?.45:.2;content.add(grid);
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
  if(visible.length>1500) {
    makeBulkBlocks(visible.filter(([,cell])=>![7,8,9,10].includes(cell&15)));
    for(const [pos,cell] of visible)if([7,8,9,10].includes(cell&15))makeBlock(pos,cell,armDirections,armStickiness,poweredPistons.has(key(pos)));
  } else for(const [pos,cell] of visible)makeBlock(pos,cell,armDirections,armStickiness,poweredPistons.has(key(pos)));
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
  if(selected&&cells.has(key(selected))&&allowed(selected))boxOutline(selected,0xffffff,detailed?1.48:1.04,detailed?1:.7);
  updatePanels(cells,owners,armDirections,info);
}
function property(name,value) {return `<div class="property"><span>${name}</span><span>${value}</span></div>`;}
function updatePanels(cells,owners,arms,info) {
  const step=info;
  $('step-badge').textContent=playbackMode==='ticks'?(tickIndex?'TICK':'INITIAL'):(step?step.stage.toUpperCase():'INITIAL');
  $('step-title').textContent=playbackMode==='ticks'?(tickIndex?`Tick ${tickIndex} complete`:'Initial configuration'):(step?step.title:'Initial configuration');
  $('step-counter').textContent=playbackMode==='ticks'?(tickIndex?`Tick ${tickIndex} / ${tickEnds.length-1}`:'Initial state'):(step?`Action ${stepIndex} / ${trace.steps.length} · tick ${step.tick}`:'Initial state');
  $('scrubber').value=playbackMode==='ticks'?tickIndex:stepIndex;
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
function setStep(index) {
  if(!trace)return;
  stepIndex=Math.max(0,Math.min(trace.steps.length,index));
  tickIndex=0;
  for(let i=1;i<tickEnds.length&&tickEnds[i]<=stepIndex;i++)tickIndex=i;
  render();
}
function setTick(index) {
  if(!trace)return;
  tickIndex=Math.max(0,Math.min(tickEnds.length-1,index));
  stepIndex=tickEnds[tickIndex];
  render();
}
function setMode(mode) {
  stopPlayback();
  playbackMode=mode;
  $('diagnostics-panel').hidden=mode!=='detailed';
  $('details-panel').hidden=mode!=='detailed';
  $('mode-ticks').classList.toggle('active',mode==='ticks');
  $('mode-detailed').classList.toggle('active',mode==='detailed');
  $('mode-ticks').setAttribute('aria-pressed',String(mode==='ticks'));
  $('mode-detailed').setAttribute('aria-pressed',String(mode==='detailed'));
  $('scrubber').max=mode==='ticks'?tickEnds.length-1:trace?.steps.length||0;
  $('end-label').textContent=mode==='ticks'?`Tick ${tickEnds.length-1}`:'Last action';
  if(trace)mode==='ticks'?setTick(tickIndex):setStep(stepIndex);
}
function advance(delta) {playbackMode==='ticks'?setTick(tickIndex+delta):setStep(stepIndex+delta);}
function manualAdvance(delta) {stopPlayback();advance(delta);}
function stopPlayback() {
  if(playing)clearInterval(playing);
  playing=null;$('play').textContent='▶';$('play').setAttribute('aria-label','Play');
}
const speedSteps=[.25,.5,.75,1,1.5,2,3,5,10,20,30];
function playbackSpeed() {return speedSteps[Number($('speed').value)];}
function playbackDelay() {return (playbackMode==='ticks'?650:330)/playbackSpeed();}
function startPlaybackTimer() {
  playing=setInterval(()=>{
    const finished=playbackMode==='ticks'?tickIndex>=tickEnds.length-1:stepIndex>=trace.steps.length;
    if(finished){stopPlayback();return;}
    advance(1);
    if(playbackMode==='ticks'?tickIndex>=tickEnds.length-1:stepIndex>=trace.steps.length)stopPlayback();
  },playbackDelay());
}
function populateTimeline() {
  tickEnds=[0];
  // A tick position is recorded only after both POWER and PISTON finish.
  trace.steps.forEach((step,i)=>{if(step.stage==='tick')tickEnds.push(i+1);});
  setMode(playbackMode);
}
function installTrace(data,title) {
  trace=data;stepIndex=0;tickIndex=0;selected=null;allBounds=computeBounds(trace);
  startBounds=computeBounds({initial:trace.initial,steps:[]});
  $('run-title').textContent=title;
  $('status').textContent='';
  $('status').classList.remove('error');
  populateTimeline();frameCamera();render();
}
async function run() {
  const ticks=Math.max(1,Math.min(1_000_000,Math.trunc(Number($('ticks').value)||200)));
  $('ticks').value=String(ticks);
  stopPlayback();
  $('status').textContent='Simulating…';
  try {
    let response;
    if(loadedBytes)response=await fetch(`/api/trace?ticks=${ticks}`,{method:'POST',headers:{'Content-Type':'application/octet-stream'},body:loadedBytes});
    else response=await fetch(`/api/demo?ticks=${ticks}`);
    if(!response.ok)throw Error(await response.text());
    installTrace(await response.json(),loadedBytes?($('file').files[0]?.name||'Loaded flyer'):'Six-block flyer');
  } catch(error) {$('status').textContent=error.message;$('status').classList.add('error');console.error(error);}
}
$('demo').onclick=()=>{loadedBytes=null;$('file').value='';run();};
$('rerun').onclick=run;
$('file').onchange=async event=>{const file=event.target.files[0];if(!file)return;loadedBytes=await file.arrayBuffer();run();};
$('scrubber').oninput=event=>{stopPlayback();playbackMode==='ticks'?setTick(Number(event.target.value)):setStep(Number(event.target.value));};
$('prev').onclick=()=>manualAdvance(-1);
$('next').onclick=()=>manualAdvance(1);
$('speed').oninput=()=>{
  const label=`${playbackSpeed()}×`;
  $('speed-label').textContent=label;
  $('speed').setAttribute('aria-valuetext',label);
  if(playing){clearInterval(playing);startPlaybackTimer();}
};
$('mode-ticks').onclick=()=>setMode('ticks');
$('mode-detailed').onclick=()=>setMode('detailed');
$('play').onclick=()=>{
  if(!trace)return;
  if(playing){stopPlayback();return;}
  if(playbackMode==='ticks'&&tickIndex===tickEnds.length-1)setTick(0);
  if(playbackMode==='detailed'&&stepIndex===trace.steps.length)setStep(0);
  $('play').textContent='Ⅱ';$('play').setAttribute('aria-label','Pause');
  startPlaybackTimer();
};
for(const id of ['show-power','show-move','show-owners','show-chunks','slice-x-on','slice-y-on','slice-z-on','slice-x','slice-y','slice-z'])$(id).addEventListener('input',render);
let drag=null;
renderer.domElement.addEventListener('pointerdown',event=>{
  if(event.button!==0)return;
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
  event.preventDefault();
  const forward=new THREE.Vector3();camera.getWorldDirection(forward);
  camera.position.addScaledVector(forward,-Math.sign(event.deltaY)*cameraMoveScale*.45);
},{passive:false});
const heldKeys=new Set();
window.addEventListener('keydown',event=>{
  if(event.target instanceof HTMLElement&&(event.target.matches('input, textarea, select')||event.target.isContentEditable))return;
  if(event.key==='ArrowRight'){event.preventDefault();manualAdvance(1);return;}
  if(event.key==='ArrowLeft'){event.preventDefault();manualAdvance(-1);return;}
  const keyName=event.key.toLowerCase();
  const moveKey=event.code==='Space'?'space':event.code==='ShiftLeft'||event.code==='ShiftRight'?'shift':keyName;
  if(['w','a','s','d','q','e','space','shift'].includes(moveKey)){
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
function animate(now){requestAnimationFrame(animate);moveCamera((now-lastFrame)/1000);lastFrame=now;renderer.render(scene,camera);}requestAnimationFrame(animate);
run();
