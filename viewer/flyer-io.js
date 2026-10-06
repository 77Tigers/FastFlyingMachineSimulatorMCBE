// Version-1 .flyer editing I/O. Coordinates in the editor may be signed;
// serialization shifts them to the nonnegative, chunk-aligned disk frame.

const MAX_SAFE=BigInt(Number.MAX_SAFE_INTEGER);
const U64_MAX=(1n<<64n)-1n;
const coord=key=>key.split(',').map(Number);
const compare=(a,b)=>a[0]-b[0]||a[1]-b[1]||a[2]-b[2];
const safe=value=>{
  if(value>MAX_SAFE)throw Error('This flyer has coordinates or counts too large for browser editing.');
  return Number(value);
};

export function parseFlyer(raw){
  const bytes=raw instanceof Uint8Array?raw:new Uint8Array(raw);
  const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
  let offset=0;
  const need=count=>{if(offset+count>bytes.length)throw Error('Truncated .flyer file');};
  const u8=()=>{need(1);return bytes[offset++];};
  const u16=()=>{need(2);const value=view.getUint16(offset,true);offset+=2;return value;};
  const varint=()=>{
    let value=0n;
    for(let i=0;i<10;i++){
      const byte=u8();value|=BigInt(byte&127)<<(7n*BigInt(i));
      if(!(byte&128)){
        if(value>U64_MAX)throw Error('Invalid .flyer integer');
        return safe(value);
      }
    }
    throw Error('Invalid .flyer integer');
  };
  const position=()=>[varint(),varint(),varint()];
  if(String.fromCharCode(u8(),u8(),u8(),u8())!=='FFLY')throw Error('Not a .flyer file');
  if(u16()!==1)throw Error('Unsupported .flyer version');
  const phaseX=u8(),phaseZ=u8();
  need(8);const rngState=view.getBigUint64(offset,true);offset+=8;
  const pushLimit=varint();
  const cells=new Map();
  const sectionCount=varint();
  for(let i=0;i<sectionCount;i++){
    const cx=varint(),cz=varint(),sy=varint(),count=varint();
    for(let j=0;j<count;j++){
      const index=u16(),cell=u16();
      const x=cx*16+(index&15),y=sy*16+(index>>8),z=cz*16+((index>>4)&15);
      if(![x,y,z].every(Number.isSafeInteger))throw Error('This flyer has coordinates too large for browser editing.');
      cells.set(`${x},${y},${z}`,cell);
    }
  }
  const pistonLists=new Map();
  const listCount=varint();
  for(let i=0;i<listCount;i++){
    const owner=position().join(','),count=varint(),members=[];
    for(let j=0;j<count;j++)members.push(position().join(','));
    pistonLists.set(owner,members);
  }
  if(offset!==bytes.length)throw Error('Unexpected trailing .flyer data');
  return {phaseX,phaseZ,rngState,pushLimit,cells,pistonLists};
}

export function serializeFlyer(flyer){
  const positions=[...flyer.cells.keys(),...flyer.pistonLists.keys(),
    ...[...flyer.pistonLists.values()].flat()];
  const mins=[Infinity,Infinity,Infinity];
  for(const key of positions){const values=coord(key);for(let i=0;i<3;i++)mins[i]=Math.min(mins[i],values[i]);}
  if(!positions.length)mins.fill(0);
  const shift=[-Math.floor(mins[0]/16)*16,-mins[1],-Math.floor(mins[2]/16)*16];
  const moved=key=>coord(key).map((value,i)=>value+shift[i]);
  const sections=new Map();
  for(const [key,cell] of flyer.cells){
    const [x,y,z]=moved(key),section=[Math.floor(x/16),Math.floor(z/16),Math.floor(y/16)];
    if(section.some(value=>value<0))throw Error('Cannot normalize this flyer');
    const sectionKey=section.join(','),index=((y&15)<<8)|((z&15)<<4)|(x&15);
    if(!sections.has(sectionKey))sections.set(sectionKey,[]);
    sections.get(sectionKey).push([index,cell]);
  }
  const bytes=[];
  const u8=value=>bytes.push(value&255);
  const u16=value=>{u8(value);u8(value>>8);};
  const varint=value=>{
    let number=BigInt(value);
    if(number<0n||number>U64_MAX)throw Error('Coordinate exceeds .flyer format range');
    while(number>=128n){u8(Number((number&127n)|128n));number>>=7n;}
    u8(Number(number));
  };
  const position=values=>values.forEach(varint);
  [...'FFLY'].forEach(char=>u8(char.charCodeAt(0)));
  u16(1);u8(flyer.phaseX);u8(flyer.phaseZ);
  for(let i=0;i<8;i++)u8(Number((flyer.rngState>>(8n*BigInt(i)))&255n));
  varint(flyer.pushLimit);
  const sortedSections=[...sections].sort((a,b)=>compare(coord(a[0]),coord(b[0])));
  varint(sortedSections.length);
  for(const [sectionKey,records] of sortedSections){
    position(coord(sectionKey));records.sort((a,b)=>a[0]-b[0]);varint(records.length);
    for(const [index,cell] of records){u16(index);u16(cell);}
  }
  const lists=[...flyer.pistonLists].filter(([,members])=>members.length)
    .sort((a,b)=>compare(moved(a[0]),moved(b[0])));
  varint(lists.length);
  for(const [owner,members] of lists){
    if(members.length>flyer.pushLimit)throw Error('Piston list exceeds push limit');
    position(moved(owner));varint(members.length);
    for(const member of members.map(moved).sort(compare))position(member);
  }
  return {bytes:new Uint8Array(bytes),shift};
}
