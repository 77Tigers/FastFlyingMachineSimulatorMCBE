// Host and guest session state machines. No DOM access: the app is reached
// through a small "port" object, and the network through a Transport.
//
// The host is authoritative. It owns the time-zero flyer and re-sends it
// whenever it changes; guests send edit requests and never mutate locally.
// Each peer runs its own simulation, so only playback state is shared.
//
// Host port:  getFlyer() -> {bytes,title,origin}; getMode() -> 'view'|'edit';
//             getPlayback() -> {tick,playing,direction,speed}; applyEdit(op)
// Guest port: loadFlyer(flyer,{first}); setMode(mode)
import * as P from './protocol.js?v=__MP_HASH__';

const POSE_EPSILON=.01,TICK_HEARTBEAT_MS=500;
const roundPoint=point=>point.map(value=>Math.round(value*100)/100);
const samePoint=(a,b)=>!!a&&!!b&&a.every((value,i)=>Math.abs(value-b[i])<POSE_EPSILON);

class Emitter{
  constructor(){this.handlers=new Map();}
  on(event,handler){
    if(!this.handlers.has(event))this.handlers.set(event,new Set());
    this.handlers.get(event).add(handler);
    return ()=>this.handlers.get(event)?.delete(handler);
  }
  // One failing listener must not stop the others, or the session.
  emit(event,value){
    for(const handler of this.handlers.get(event)||[]){
      try{handler(value);}catch(error){console.error(`Multiplayer: ${event} handler failed`,error);}
    }
  }
}
// Network callbacks run outside the app's control: report errors, never throw.
const guarded=(label,fn)=>(...args)=>{
  try{return fn(...args);}catch(error){console.error(`Multiplayer: ${label} failed`,error);}
};

class Session extends Emitter{
  constructor({transport,port,room}){
    super();
    this.transport=transport;this.port=port;this.room=room;
    this.ended=false;this.lastPose=null;
  }
  get selfId(){return this.transport.selfId;}
  async end(reason){
    if(this.ended)return;
    this.ended=true;
    try{await this.transport.leave();}catch(error){console.warn('Leaving the room failed',error);}
    this.emit('ended',{reason});
  }
}

export class HostSession extends Session{
  constructor(options){
    super(options);
    this.role='host';
    this.guests=new Map();   // peerId -> {name, pose}
    this.flyerSignature=null;this.mode=null;
    this.playback=null;this.playbackSentAt=-Infinity;this.posesDirty=false;
  }
  async start(){
    const t=this.transport;
    t.onMessage=guarded('host message',(raw,peerId)=>this.receive(raw,peerId));
    t.onPeerLeave=guarded('peer leave',peerId=>this.removeGuest(peerId));
    await t.join(this.room);
    this.flyerSignature=P.flyerSignature(P.encodeFlyer(this.port.getFlyer()));
    this.mode=this.port.getMode();
    this.emitRoster();
  }
  players(){
    return [{id:this.selfId,name:P.HOST_NAME},...[...this.guests].map(([id,guest])=>({id,name:guest.name}))];
  }
  emitRoster(){
    const players=this.players();
    this.emit('roster',players.map(player=>({...player,self:player.id===this.selfId})));
    return players;
  }
  broadcast(message){this.transport.send(message);}
  system(text){this.broadcast({t:P.SYSTEM,text});this.emit('chat',{system:true,text});}
  uniqueName(raw){
    let base=P.cleanName(raw);
    if(P.nameProblem(base))base='Guest';
    const taken=new Set([P.HOST_NAME,...[...this.guests.values()].map(guest=>guest.name)].map(name=>name.toUpperCase()));
    if(!taken.has(base.toUpperCase()))return base;
    for(let n=2;;n++){const name=`${base} (${n})`;if(!taken.has(name.toUpperCase()))return name;}
  }
  receive(raw,peerId){
    if(this.ended)return;
    const message=P.parseGuestMessage(raw);
    if(!message)return;
    if(message.t===P.HELLO){this.welcome(peerId,message);return;}
    const guest=this.guests.get(peerId);
    if(!guest)return;
    if(message.t===P.POSE){
      const pose=roundPoint(message.p);
      if(!samePoint(pose,guest.pose)){guest.pose=pose;this.posesDirty=true;}
    }else if(message.t===P.CHAT){
      const text=P.cleanChat(message.text);
      if(text)this.chatLine(guest.name,text);
    }else if(message.t===P.EDIT){
      // Guests may only edit while the host itself is editing.
      if(this.port.getMode()==='edit')this.port.applyEdit(message.op);
    }
  }
  welcome(peerId,{v,name}){
    if(this.guests.has(peerId))return;
    if(v!==P.PROTOCOL_VERSION){
      this.transport.send({t:P.REJECT,reason:'Your page is a different version from the host’s. Reload both pages and try again.'},peerId);
      return;
    }
    const guest={name:this.uniqueName(name),pose:null};
    this.guests.set(peerId,guest);
    this.transport.send({t:P.WELCOME,you:{id:peerId,name:guest.name},
      flyer:P.encodeFlyer(this.port.getFlyer()),mode:this.port.getMode(),playback:this.port.getPlayback()},peerId);
    this.broadcast({t:P.ROSTER,players:this.emitRoster()});
    this.system(`${guest.name} joined`);
    this.posesDirty=true;
  }
  removeGuest(peerId){
    const guest=this.guests.get(peerId);
    if(!guest||this.ended)return;
    this.guests.delete(peerId);
    this.broadcast({t:P.ROSTER,players:this.emitRoster()});
    this.system(`${guest.name} left`);
    this.posesDirty=true;
  }
  chatLine(from,text){this.broadcast({t:P.CHAT_LINE,from,text});this.emit('chat',{from,text});}
  sendChat(raw){const text=P.cleanChat(raw);if(text&&!this.ended)this.chatLine(P.HOST_NAME,text);}
  /** Call whenever the time-zero flyer, its title or origin may have changed. */
  flyerChanged(){
    if(this.ended)return;
    const flyer=P.encodeFlyer(this.port.getFlyer()),signature=P.flyerSignature(flyer);
    if(signature===this.flyerSignature)return;
    this.flyerSignature=signature;
    this.broadcast({t:P.FLYER,flyer});
  }
  modeChanged(){
    const mode=this.port.getMode();
    if(this.ended||mode===this.mode)return;
    this.mode=mode;this.broadcast({t:P.MODE,mode});
  }
  /** Periodic: shares playback state and everyone's positions. */
  publish(now,cameraPosition){
    if(this.ended)return;
    const state=this.port.getPlayback(),last=this.playback;
    const controlsChanged=!last||state.playing!==last.playing||state.direction!==last.direction||state.speed!==last.speed;
    const tickChanged=!last||state.tick!==last.tick;
    // While playing, guests run their own clocks; the tick is only a correction.
    if(controlsChanged||(tickChanged&&(!state.playing||now-this.playbackSentAt>=TICK_HEARTBEAT_MS))){
      this.playback={...state};this.playbackSentAt=now;
      this.broadcast({t:P.PLAYBACK,state:this.playback});
    }
    const pose=roundPoint(cameraPosition);
    if(!samePoint(pose,this.lastPose)){this.lastPose=pose;this.posesDirty=true;}
    if(this.posesDirty){
      this.posesDirty=false;
      const poses=[[this.selfId,...this.lastPose]];
      for(const [id,guest] of this.guests)if(guest.pose)poses.push([id,...guest.pose]);
      this.broadcast({t:P.POSES,poses});
      this.emit('poses',poses.filter(([id])=>id!==this.selfId));
    }
  }
  async stop(){
    if(this.ended)return;
    this.broadcast({t:P.END});
    await this.end('You stopped hosting.');
  }
}

export class GuestSession extends Session{
  constructor({hostId,name,...options}){
    super(options);
    this.role='guest';this.hostId=hostId;this.name=name;
    this.welcomed=false;this.helloSent=false;this.flyerSignature=null;
    this.hostPlayback=null;this.players=[];
  }
  async start(){
    const t=this.transport;
    t.onPeerJoin=guarded('peer join',peerId=>{if(peerId===this.hostId)this.hello();});
    t.onPeerLeave=guarded('peer leave',peerId=>{if(peerId===this.hostId)this.end(this.welcomed?'The host left the session.':'Could not reach the host.');});
    t.onMessage=guarded('guest message',(raw,peerId)=>{if(peerId===this.hostId)this.receive(raw);});
    await t.join(this.room);
  }
  hello(){
    if(this.helloSent||this.ended)return;
    this.helloSent=true;
    this.transport.send({t:P.HELLO,v:P.PROTOCOL_VERSION,name:this.name},this.hostId);
  }
  loadFlyer(flyer,first){
    const signature=P.flyerSignature(flyer);
    if(!first&&signature===this.flyerSignature)return;
    this.flyerSignature=signature;
    this.port.loadFlyer(P.decodeFlyer(flyer),{first});
  }
  receive(raw){
    if(this.ended)return;
    const message=P.parseHostMessage(raw);
    if(!message)return;
    if(message.t===P.WELCOME){
      if(this.welcomed)return;
      this.welcomed=true;this.name=message.you.name;
      this.loadFlyer(message.flyer,true);
      this.port.setMode(message.mode);
      this.emit('welcome',{name:this.name});
      this.hostPlayback=message.playback;this.emit('playback',this.hostPlayback);
      return;
    }
    if(message.t===P.REJECT){this.end(message.reason);return;}
    if(message.t===P.END){this.end('The host ended the session.');return;}
    if(!this.welcomed)return;
    switch(message.t){
      case P.FLYER:this.loadFlyer(message.flyer,false);break;
      case P.MODE:this.port.setMode(message.mode);break;
      case P.PLAYBACK:this.hostPlayback=message.state;this.emit('playback',message.state);break;
      case P.ROSTER:
        this.players=message.players;
        this.emit('roster',message.players.map(player=>({...player,self:player.id===this.selfId})));
        break;
      case P.POSES:this.emit('poses',message.poses.filter(([id])=>id!==this.selfId));break;
      case P.CHAT_LINE:this.emit('chat',{from:message.from,text:message.text});break;
      case P.SYSTEM:this.emit('chat',{system:true,text:message.text});break;
    }
  }
  sendChat(raw){
    const text=P.cleanChat(raw);
    if(text&&this.welcomed&&!this.ended)this.transport.send({t:P.CHAT,text},this.hostId);
  }
  requestEdit(op){if(this.welcomed&&!this.ended)this.transport.send({t:P.EDIT,op},this.hostId);}
  publish(now,cameraPosition){
    if(!this.welcomed||this.ended)return;
    const pose=roundPoint(cameraPosition);
    if(samePoint(pose,this.lastPose))return;
    this.lastPose=pose;this.transport.send({t:P.POSE,p:pose},this.hostId);
  }
  async stop(){await this.end('You left the session.');}
}
