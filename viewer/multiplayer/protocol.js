// Wire protocol shared by host and guests. Every message is a small JSON
// object tagged with `t`. Peers validate everything they receive: a guest's
// messages are untrusted input to the host, and vice versa.

export const PROTOCOL_VERSION=1;
export const HOST_NAME='HOST';
export const MAX_NAME_LENGTH=24;
export const MAX_CHAT_LENGTH=300;
export const MAX_PLACE_CELLS=64;

// Guest -> host
export const HELLO='hello',POSE='pose',CHAT='chat',EDIT='edit';
// Host -> guest
export const WELCOME='welcome',REJECT='reject',FLYER='flyer',MODE='mode',PLAYBACK='playback',
  ROSTER='roster',POSES='poses',CHAT_LINE='chat-line',SYSTEM='system',END='end';

const isObject=value=>value!==null&&typeof value==='object'&&!Array.isArray(value);
const isInt=value=>Number.isSafeInteger(value);
const isPos=value=>Array.isArray(value)&&value.length===3&&value.every(isInt);
const isPoint=value=>Array.isArray(value)&&value.length===3&&value.every(Number.isFinite);
const isString=(value,max)=>typeof value==='string'&&value.length<=max;
const isMode=value=>value==='view'||value==='edit';

export function cleanName(raw){
  // Collapse whitespace and drop control characters; names are display-only.
  return String(raw??'').replace(/[\x00-\x1f\x7f]/g,'').replace(/\s+/g,' ').trim().slice(0,MAX_NAME_LENGTH);
}
export function nameProblem(name){
  if(!name)return 'Enter a name.';
  if(name.toUpperCase()===HOST_NAME)return `“${HOST_NAME}” is reserved for the host.`;
  return null;
}
export function cleanChat(raw){
  return String(raw??'').replace(/[\x00-\x1f\x7f]/g,' ').trim().slice(0,MAX_CHAT_LENGTH);
}

export function encodeBytes(bytes){
  let binary='';
  for(let i=0;i<bytes.length;i+=0x8000)binary+=String.fromCharCode(...bytes.subarray(i,i+0x8000));
  return btoa(binary);
}
export function decodeBytes(text){
  const binary=atob(text),bytes=new Uint8Array(binary.length);
  for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);
  return bytes;
}
export function encodeFlyer({bytes,title,origin}){return {bytes:encodeBytes(bytes),title,origin:[...origin]};}
export function decodeFlyer(flyer){return {bytes:decodeBytes(flyer.bytes),title:flyer.title,origin:[...flyer.origin]};}
// Cheap identity for "did the shared flyer actually change?".
export function flyerSignature(flyer){return `${flyer.title}\u0000${flyer.origin.join(',')}\u0000${flyer.bytes}`;}

function validFlyer(flyer){
  return isObject(flyer)&&isString(flyer.bytes,4_000_000)&&isString(flyer.title,200)&&isPos(flyer.origin);
}
function validPlayback(state){
  return isObject(state)&&isInt(state.tick)&&state.tick>=0&&typeof state.playing==='boolean'
    &&(state.direction===1||state.direction===-1)&&Number.isFinite(state.speed);
}
function validEdit(op){
  if(!isObject(op))return false;
  if(op.op==='place')return Array.isArray(op.positions)&&op.positions.length>0&&op.positions.length<=MAX_PLACE_CELLS
    &&op.positions.every(isPos)&&isInt(op.cell)&&op.cell>=0&&op.cell<=0xffff;
  if(op.op==='remove'||op.op==='cycle')return isPos(op.pos);
  return false;
}

const fromGuest={
  // Any version parses, so the host can explain a mismatch instead of ignoring it.
  [HELLO]:m=>isInt(m.v)&&isString(m.name,200),
  [POSE]:m=>isPoint(m.p),
  [CHAT]:m=>isString(m.text,MAX_CHAT_LENGTH*4),
  [EDIT]:m=>validEdit(m.op),
};
const fromHost={
  [WELCOME]:m=>isObject(m.you)&&typeof m.you.name==='string'&&validFlyer(m.flyer)&&isMode(m.mode)&&validPlayback(m.playback),
  [REJECT]:m=>typeof m.reason==='string',
  [FLYER]:m=>validFlyer(m.flyer),
  [MODE]:m=>isMode(m.mode),
  [PLAYBACK]:m=>validPlayback(m.state),
  [ROSTER]:m=>Array.isArray(m.players)&&m.players.every(p=>isObject(p)&&typeof p.id==='string'&&typeof p.name==='string'),
  [POSES]:m=>Array.isArray(m.poses)&&m.poses.every(p=>Array.isArray(p)&&p.length===4&&typeof p[0]==='string'&&isPoint(p.slice(1))),
  [CHAT_LINE]:m=>typeof m.from==='string'&&typeof m.text==='string',
  [SYSTEM]:m=>typeof m.text==='string',
  [END]:()=>true,
};
function validator(table){
  return message=>isObject(message)&&Object.hasOwn(table,message.t)&&table[message.t](message)?message:null;
}
/** Returns the message if it is a well-formed guest->host message, else null. */
export const parseGuestMessage=validator(fromGuest);
/** Returns the message if it is a well-formed host->guest message, else null. */
export const parseHostMessage=validator(fromHost);

/** Invite links carry the room and the host's peer id, so guests only trust that peer. */
export function inviteUrl(base,{room,host}){
  const url=new URL(base);
  url.search='';url.hash='';
  url.searchParams.set('room',room);url.searchParams.set('host',host);
  return url.toString();
}
export function readInvite(search){
  const params=new URLSearchParams(search);
  const room=params.get('room'),host=params.get('host');
  return room&&host&&/^[\w-]{4,64}$/.test(room)&&/^[\w-]{4,128}$/.test(host)?{room,host}:null;
}
export function newRoomId(){
  const alphabet='abcdefghjkmnpqrstuvwxyz23456789',bytes=crypto.getRandomValues(new Uint8Array(12));
  return [...bytes].map(byte=>alphabet[byte%alphabet.length]).join('');
}
