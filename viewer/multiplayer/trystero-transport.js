// WebRTC transport. Trystero exchanges connection offers over public Nostr
// relays, then all traffic flows directly between browsers.
import {joinRoom,selfId} from '@trystero-p2p/nostr';
import {TransportBase} from './transport.js?v=__MP_HASH__';

const DEFAULT_STUN=[{urls:['stun:stun.l.google.com:19302','stun:stun.cloudflare.com:3478']}];
const RELAY_CHECK_MS=4000;

// Keeps the preferred order but drops relays that do not answer, so Trystero
// never sits retrying a dead one. Each dead relay costs one console line here.
async function liveRelays(urls,count){
  const alive=await Promise.all(urls.map(url=>new Promise(resolve=>{
    let socket;
    const finish=ok=>{clearTimeout(timer);try{socket?.close();}catch{/* already closed */}resolve(ok);};
    const timer=setTimeout(()=>finish(false),RELAY_CHECK_MS);
    try{socket=new WebSocket(url);}catch{finish(false);return;}
    socket.onopen=()=>finish(true);
    socket.onerror=()=>finish(false);
  })));
  const chosen=urls.filter((url,i)=>alive[i]).slice(0,count);
  const skipped=urls.filter((url,i)=>!alive[i]);
  if(skipped.length)console.warn('Multiplayer: skipping unreachable relays',skipped);
  if(!chosen.length)throw Error('Could not reach any signalling relay. Check your internet connection.');
  return chosen;
}

class TrysteroTransport extends TransportBase{
  constructor({appId,nostrRelays,relayCount=5,turnServers=[]}){
    super(selfId);
    Object.assign(this,{appId,nostrRelays,relayCount,turnServers});
    this.room=null;this.action=null;
  }
  async join(roomId){
    const urls=this.nostrRelays?.length?await liveRelays(this.nostrRelays,this.relayCount):undefined;
    // The room id doubles as the password, so relays only see encrypted offers.
    this.room=joinRoom({appId:this.appId,password:roomId,relayConfig:urls&&{urls},
      rtcConfig:{iceServers:[...DEFAULT_STUN,...this.turnServers]}},roomId);
    this.action=this.room.makeAction('ff');
    this.action.onMessage=(data,{peerId})=>this.onMessage(data,peerId);
    this.room.onPeerJoin=peerId=>this.onPeerJoin(peerId);
    this.room.onPeerLeave=peerId=>this.onPeerLeave(peerId);
  }
  send(message,peerId){
    try{
      this.action?.send(message,peerId===undefined?undefined:{target:peerId})
        .catch(error=>console.warn('Multiplayer: send failed',error));
    }catch(error){console.warn('Multiplayer: send failed',error);}
  }
  async leave(){
    const room=this.room;this.room=null;this.action=null;
    await room?.leave();
  }
}

export function createTransport(options){return new TrysteroTransport(options);}
