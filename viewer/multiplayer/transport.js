// Transport: the only networking surface the session logic depends on.
//
// interface Transport {
//   readonly selfId: string;                       // stable for this page load
//   join(roomId: string): Promise<void>;
//   send(message: object, peerId?: string): void;  // omit peerId to broadcast
//   onMessage: (message: object, peerId: string) => void;
//   onPeerJoin: (peerId: string) => void;
//   onPeerLeave: (peerId: string) => void;
//   leave(): Promise<void>;
// }
//
// Messages are plain JSON objects. Delivery to each peer must be reliable and
// ordered. Implementations live in their own modules and are loaded lazily, so
// a page only downloads the backend it uses.

const registry={
  trystero:()=>import('./trystero-transport.js?v=__MP_HASH__'),
  local:()=>import('./local-transport.js?v=__MP_HASH__'),
};

export function transportNames(){return Object.keys(registry);}

export async function createTransport(name,options={}){
  if(!Object.hasOwn(registry,name))throw Error(`Unknown multiplayer transport “${name}”`);
  const module=await registry[name]();
  return module.createTransport(options);
}

/** Base for implementations: default no-op handlers, overwritten by the session. */
export class TransportBase{
  constructor(selfId){
    this.selfId=selfId;
    this.onMessage=()=>{};this.onPeerJoin=()=>{};this.onPeerLeave=()=>{};
  }
}
