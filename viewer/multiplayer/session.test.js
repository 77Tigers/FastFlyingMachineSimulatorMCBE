// Run with: npm test --prefix viewer
// Sessions talk over the real BroadcastChannel transport, with fake app ports.
import test from 'node:test';
import assert from 'node:assert/strict';
import {HostSession,GuestSession} from './session.js?v=__MP_HASH__';
import {createTransport} from './local-transport.js?v=__MP_HASH__';
import * as P from './protocol.js?v=__MP_HASH__';

const until=async(check,label='condition')=>{
  for(let i=0;i<200;i++){if(check())return;await new Promise(resolve=>setTimeout(resolve,5));}
  assert.fail(`Timed out waiting for ${label}`);
};
let rooms=0;
const nextRoom=()=>`test-room-${process.pid}-${rooms++}`;

function hostPort(){
  return {
    flyer:{bytes:new Uint8Array([1,2,3]),title:'Demo',origin:[0,0,0]},
    mode:'view',edits:[],
    playback:{tick:0,playing:false,direction:1,speed:50},
    getFlyer(){return this.flyer;},getMode(){return this.mode;},
    getPlayback(){return this.playback;},applyEdit(op){this.edits.push(op);},
  };
}
function guestPort(){
  return {flyers:[],mode:null,loadFlyer(flyer,{first}){this.flyers.push({...flyer,first});},setMode(mode){this.mode=mode;}};
}
function record(session){
  const log={chat:[],roster:[],poses:[],playback:[],ended:null};
  session.on('chat',line=>log.chat.push(line));
  session.on('roster',players=>log.roster=players);
  session.on('poses',poses=>log.poses=poses);
  session.on('playback',state=>log.playback.push(state));
  session.on('ended',value=>log.ended=value);
  return log;
}
async function startHost(room){
  const port=hostPort(),session=new HostSession({transport:createTransport({heartbeat:false}),port,room});
  const log=record(session);await session.start();
  return {port,session,log};
}
async function startGuest(room,host,name){
  const port=guestPort(),session=new GuestSession({transport:createTransport({heartbeat:false}),port,room,hostId:host.session.selfId,name});
  const log=record(session);await session.start();
  await until(()=>session.welcomed,`${name} welcome`);
  return {port,session,log};
}

test('guests are welcomed with the flyer, mode and playback, and named uniquely',async()=>{
  const room=nextRoom(),host=await startHost(room);
  host.port.mode='edit';
  const bob=await startGuest(room,host,'  Bob  ');
  const bob2=await startGuest(room,host,'bob');
  const sneaky=await startGuest(room,host,'host');
  assert.equal(bob.session.name,'Bob');
  assert.equal(bob2.session.name,'bob (2)');
  assert.equal(sneaky.session.name,'Guest');
  assert.deepEqual([...bob.port.flyers[0].bytes],[1,2,3]);
  assert.equal(bob.port.flyers[0].first,true);
  assert.equal(bob.port.mode,'edit');
  assert.equal(bob.log.playback[0].tick,0);
  await until(()=>bob.log.roster.length===4,'roster');
  assert.deepEqual(bob.log.roster.map(p=>p.name),['HOST','Bob','bob (2)','Guest']);
  assert.equal(bob.log.roster.find(p=>p.self).name,'Bob');
  assert.deepEqual(host.log.chat.map(line=>line.text),['Bob joined','bob (2) joined','Guest joined']);
  await Promise.all([host.session.stop(),bob.session.stop(),bob2.session.stop(),sneaky.session.stop()]);
});

test('host shares flyer and mode changes only when they really change',async()=>{
  const room=nextRoom(),host=await startHost(room),guest=await startGuest(room,host,'Ann');
  host.session.flyerChanged();host.session.modeChanged();
  host.port.flyer={bytes:new Uint8Array([9]),title:'Demo',origin:[0,0,0]};host.session.flyerChanged();
  host.port.flyer={bytes:new Uint8Array([9]),title:'Renamed',origin:[0,0,0]};host.session.flyerChanged();
  host.port.mode='edit';host.session.modeChanged();
  await until(()=>guest.port.mode==='edit','mode');
  assert.deepEqual(guest.port.flyers.map(f=>[f.title,[...f.bytes],f.first]),
    [['Demo',[1,2,3],true],['Demo',[9],false],['Renamed',[9],false]]);
  await Promise.all([host.session.stop(),guest.session.stop()]);
});

test('guest edits apply only while the host is editing',async()=>{
  const room=nextRoom(),host=await startHost(room),guest=await startGuest(room,host,'Ed');
  guest.session.requestEdit({op:'remove',pos:[1,2,3]});
  guest.session.requestEdit({op:'bogus'});
  // Messages are ordered, so a chat line acts as a delivery barrier.
  guest.session.sendChat('barrier 1');
  await until(()=>host.log.chat.some(line=>line.text==='barrier 1'),'first barrier');
  host.port.mode='edit';
  guest.session.requestEdit({op:'place',positions:[[0,0,0],[1,0,0]],cell:1});
  guest.session.sendChat('barrier 2');
  await until(()=>host.log.chat.some(line=>line.text==='barrier 2'),'second barrier');
  assert.deepEqual(host.port.edits,[{op:'place',positions:[[0,0,0],[1,0,0]],cell:1}]);
  await Promise.all([host.session.stop(),guest.session.stop()]);
});

test('chat, poses and leave/end notifications reach everyone',async()=>{
  const room=nextRoom(),host=await startHost(room);
  const a=await startGuest(room,host,'A'),b=await startGuest(room,host,'B');
  a.session.sendChat('  hi\nthere  ');
  host.session.sendChat('welcome');
  await until(()=>b.log.chat.filter(line=>!line.system).length===2,'chat');
  // A's line travels via the host, so it may arrive after the host's own line.
  const lines=b.log.chat.filter(line=>!line.system).map(line=>`${line.from}: ${line.text}`).sort();
  assert.deepEqual(lines,['A: hi there','HOST: welcome']);
  a.session.publish(0,[1.234,2,3]);
  await until(()=>host.session.guests.get(a.session.selfId).pose,'pose');
  host.session.publish(0,[0,0,0]);
  await until(()=>b.log.poses.length===2,'poses');
  assert.deepEqual(b.log.poses.map(p=>p[0]).sort(),[host.session.selfId,a.session.selfId].sort());
  assert.deepEqual(b.log.poses.find(p=>p[0]===a.session.selfId).slice(1),[1.23,2,3]);
  await a.session.stop();
  await until(()=>b.log.chat.some(line=>line.text==='A left'),'leave');
  await host.session.stop();
  await until(()=>b.log.ended,'end');
  assert.equal(b.log.ended.reason,'The host ended the session.');
});

test('playback ticks are rate limited while playing but control changes are immediate',async()=>{
  const room=nextRoom(),host=await startHost(room),guest=await startGuest(room,host,'P');
  const sent=()=>guest.log.playback.length;
  host.port.playback={tick:0,playing:true,direction:1,speed:50};host.session.publish(1000,[0,0,0]);
  await until(()=>sent()===2,'play');
  host.port.playback={tick:5,playing:true,direction:1,speed:50};host.session.publish(1100,[0,0,0]);
  host.port.playback={tick:9,playing:true,direction:1,speed:50};host.session.publish(1600,[0,0,0]);
  host.port.playback={tick:9,playing:false,direction:1,speed:50};host.session.publish(1650,[0,0,0]);
  await until(()=>sent()===4,'pause');
  assert.deepEqual(guest.log.playback.map(s=>[s.tick,s.playing]),[[0,false],[0,true],[9,true],[9,false]]);
  await Promise.all([host.session.stop(),guest.session.stop()]);
});

test('protocol rejects malformed messages and version mismatches',async()=>{
  assert.equal(P.parseGuestMessage({t:'edit',op:{op:'place',positions:[[0,0,0.5]],cell:1}}),null);
  assert.equal(P.parseGuestMessage({t:'edit',op:{op:'place',positions:Array(65).fill([0,0,0]),cell:1}}),null);
  assert.equal(P.parseHostMessage({t:'flyer',flyer:{bytes:'',title:'x',origin:[0,0]}}),null);
  assert.equal(P.parseHostMessage({t:'__proto__'}),null);
  assert.deepEqual([...P.decodeBytes(P.encodeBytes(new Uint8Array([0,255,7])))],[0,255,7]);
  assert.deepEqual(P.readInvite('?room=abcd2345&host=peer-1'),{room:'abcd2345',host:'peer-1'});
  assert.equal(P.readInvite('?room=a b&host=x'),null);
  const room=nextRoom(),host=await startHost(room);
  const transport=createTransport({heartbeat:false});
  let rejected=null;
  transport.onMessage=message=>{if(message.t===P.REJECT)rejected=message.reason;};
  transport.onPeerJoin=peerId=>transport.send({t:P.HELLO,v:P.PROTOCOL_VERSION+1,name:'Old'},peerId);
  await transport.join(room);
  await until(()=>rejected,'reject');
  assert.equal(host.session.guests.size,0);
  await Promise.all([host.session.stop(),transport.leave()]);
});
