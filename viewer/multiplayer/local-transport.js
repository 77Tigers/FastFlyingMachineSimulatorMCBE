// Same-browser transport over BroadcastChannel: lets two tabs play together
// with no network, and runs the session tests under Node.
import {TransportBase} from './transport.js?v=__MP_HASH__';

const randomId=()=>[...crypto.getRandomValues(new Uint8Array(9))].map(b=>b.toString(36).padStart(2,'0')).join('');
const HEARTBEAT_MS=1000,TIMEOUT_MS=3500;

class LocalTransport extends TransportBase{
  constructor({appId='fastflyer',heartbeat=true}={}){
    super(randomId());
    this.appId=appId;this.heartbeat=heartbeat;
    this.channel=null;this.peers=new Map();this.timer=null;
    this.onPageHide=()=>this.post({kind:'bye'});
  }
  post(packet){this.channel?.postMessage({...packet,from:this.selfId});}
  seen(peerId){
    const known=this.peers.has(peerId);
    this.peers.set(peerId,Date.now());
    if(!known){this.post({kind:'here',to:peerId});this.onPeerJoin(peerId);}
  }
  drop(peerId){if(this.peers.delete(peerId))this.onPeerLeave(peerId);}
  async join(roomId){
    this.channel=new BroadcastChannel(`fastflyer:${this.appId}:${roomId}`);
    this.channel.onmessage=({data})=>{
      if(!data||data.from===this.selfId||(data.to&&data.to!==this.selfId))return;
      if(data.kind==='bye'){this.drop(data.from);return;}
      this.seen(data.from);
      if(data.kind==='message')this.onMessage(data.message,data.from);
    };
    this.post({kind:'here'});
    if(this.heartbeat){
      this.timer=setInterval(()=>{
        this.post({kind:'ping'});
        for(const [peerId,last] of this.peers)if(Date.now()-last>TIMEOUT_MS)this.drop(peerId);
      },HEARTBEAT_MS);
    }
    globalThis.addEventListener?.('pagehide',this.onPageHide);
  }
  send(message,peerId){this.post({kind:'message',message,to:peerId});}
  async leave(){
    if(!this.channel)return;
    this.post({kind:'bye'});
    clearInterval(this.timer);globalThis.removeEventListener?.('pagehide',this.onPageHide);
    this.channel.close();this.channel=null;this.peers.clear();
  }
}

export function createTransport(options){return new LocalTransport(options);}
