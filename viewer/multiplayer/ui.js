// Multiplayer UI: hosting/joining, the session panel, chat and nametags.
// Talks to the viewer only through the port built in app.js.
import {multiplayerConfig} from './config.js?v=__MP_HASH__';
import {createTransport,transportNames} from './transport.js?v=__MP_HASH__';
import {HostSession,GuestSession} from './session.js?v=__MP_HASH__';
import {readInvite,inviteUrl,newRoomId,cleanName,nameProblem,HOST_NAME} from './protocol.js?v=__MP_HASH__';

const $=id=>document.getElementById(id);
const PUBLISH_MS=100,HOST_SEARCH_HINT_MS=15000,CHAT_FADE_MS=10000,CHAT_LIMIT=100;
const NAME_STORAGE_KEY='fastflyer-multiplayer-name';

function chosenTransport(){
  const requested=new URLSearchParams(location.search).get('transport');
  return transportNames().includes(requested)?requested:multiplayerConfig.transport;
}
function storedName(){try{return localStorage.getItem(NAME_STORAGE_KEY)||'';}catch{return '';}}
function storeName(name){try{localStorage.setItem(NAME_STORAGE_KEY,name);}catch{/* per-viewer convenience only */}}
function clearInviteFromUrl(){
  const url=new URL(location.href);
  for(const name of ['room','host','transport'])url.searchParams.delete(name);
  history.replaceState(null,'',url);
}

function createChat(port,send){
  const box=$('chat'),log=$('chat-log'),input=$('chat-input');
  let enabled=false,isOpen=false,refocusScene=false;
  function add({from,text,system=false}){
    const line=document.createElement('div');line.className=system?'chat-line system':'chat-line';
    if(from){const name=document.createElement('span');name.className=from===HOST_NAME?'chat-name host':'chat-name';name.textContent=`${from}:`;line.append(name,' ');}
    line.append(text);log.append(line);
    while(log.children.length>CHAT_LIMIT)log.firstElementChild.remove();
    setTimeout(()=>line.classList.add('faded'),CHAT_FADE_MS);
    log.scrollTop=log.scrollHeight;
  }
  function open(){
    if(!enabled||isOpen)return false;
    isOpen=true;refocusScene=port.sceneFocused();
    port.releaseMovementKeys();
    box.classList.add('open');input.hidden=false;input.focus({preventScroll:true});
    log.scrollTop=log.scrollHeight;
    return true;
  }
  function close(refocus=true){
    if(!isOpen)return;
    isOpen=false;box.classList.remove('open');input.hidden=true;input.blur();
    if(refocus&&refocusScene)port.focusScene();
  }
  input.addEventListener('keydown',event=>{
    // Keep chat typing away from the viewer's shortcuts, Esc included.
    event.stopPropagation();
    if(event.key==='Escape'){event.preventDefault();close();}
    else if(event.key==='Enter'){
      event.preventDefault();
      const text=input.value.trim();
      if(!text){close();return;}
      send(text);input.value='';
    }
  });
  input.addEventListener('blur',()=>close(false));
  port.setChatOpener(open);
  return {
    add,
    setEnabled(value){enabled=value;box.hidden=!value&&!log.children.length;if(!value)close(false);},
  };
}

function createNametags(port){
  const layer=$('nametag-layer'),tags=new Map(); // id -> {element,position}
  let names=new Map();
  function tag(id){
    if(!tags.has(id)){
      const element=document.createElement('span');element.className='nametag';element.hidden=true;
      layer.append(element);tags.set(id,{element,position:null});
    }
    return tags.get(id);
  }
  function label(id,entry){
    const name=names.get(id)||'…';
    entry.element.textContent=name;entry.element.classList.toggle('host',name===HOST_NAME);
  }
  port.onFrame(()=>{
    for(const {element,position} of tags.values()){
      if(!position){element.hidden=true;continue;}
      const view=port.projectToScreen([position[0],position[1]+.45,position[2]]);
      if(!view.visible||view.distance>400){element.hidden=true;continue;}
      element.hidden=false;
      element.style.left=`${view.x}px`;element.style.top=`${view.y}px`;
      // Shrinks with distance like the piston labels, but never vanishes entirely.
      element.style.transform=`translate(-50%,-100%) scale(${Math.max(.18,Math.min(1.1,10/Math.max(view.distance,1)))})`;
      element.style.zIndex=String(Math.round((400-view.distance)*100));
    }
  });
  return {
    setRoster(players){
      names=new Map(players.map(player=>[player.id,player.name]));
      for(const [id,entry] of tags){if(names.has(id))label(id,entry);else{entry.element.remove();tags.delete(id);}}
    },
    setPoses(poses){
      const present=new Set();
      for(const [id,x,y,z] of poses){present.add(id);const entry=tag(id);entry.position=[x,y,z];label(id,entry);}
      for(const [id,entry] of tags)if(!present.has(id)){entry.element.remove();tags.delete(id);}
    },
    clear(){layer.replaceChildren();tags.clear();names=new Map();},
  };
}

function askName(){
  const dialog=$('join-dialog'),form=$('join-form'),input=$('join-name'),error=$('join-error');
  input.value=storedName();error.textContent='';
  return new Promise(resolve=>{
    const finish=value=>{form.onsubmit=null;$('join-cancel').onclick=null;dialog.oncancel=null;dialog.close();resolve(value);};
    form.onsubmit=event=>{
      event.preventDefault();
      const name=cleanName(input.value),problem=nameProblem(name);
      if(problem){error.textContent=problem;input.focus();return;}
      storeName(name);finish(name);
    };
    $('join-cancel').onclick=()=>finish(null);
    dialog.oncancel=event=>{event.preventDefault();finish(null);};
    dialog.showModal();input.focus();input.select();
  });
}

export function setupMultiplayer(port){
  const invite=readInvite(location.search);
  const button=$('host-session'),panel=$('multiplayer-panel'),followHost=$('follow-host');
  const chat=createChat(port,text=>session?.sendChat(text));
  const nametags=createNametags(port);
  let session=null,role=null,inviteLink='',publishTimer=null,searchTimer=null,cleanups=[];
  chat.setEnabled(false);

  function setButton(label,{disabled=false,danger=false}={}){
    button.textContent=label;button.disabled=disabled;button.classList.toggle('danger',danger);
  }
  function showPanel(statusText){
    panel.hidden=false;$('mp-status').textContent=statusText;
    $('mp-invite').value=inviteLink;$('mp-invite-row').hidden=!inviteLink;
  }
  function showPlayers(players){
    const list=$('mp-players');list.replaceChildren();
    for(const player of players){
      const item=document.createElement('li');
      item.textContent=player.self?`${player.name} (you)`:player.name;
      if(player.name===HOST_NAME)item.className='host';
      list.append(item);
    }
    $('mp-count').textContent=`${players.length} ${players.length===1?'player':'players'}`;
  }
  function listen(target,event,handler){target.addEventListener(event,handler);cleanups.push(()=>target.removeEventListener(event,handler));}
  function attach(active){
    session=active;
    cleanups.push(
      active.on('roster',players=>{showPlayers(players);nametags.setRoster(players);}),
      active.on('poses',poses=>nametags.setPoses(poses)),
      active.on('chat',line=>chat.add(line)),
      active.on('ended',({reason})=>teardown(reason)),
    );
    publishTimer=setInterval(()=>{
      try{active.publish(performance.now(),port.cameraPosition());}
      catch(error){console.error('Multiplayer: publish failed',error);}
    },PUBLISH_MS);
  }
  function teardown(reason){
    const wasGuest=role==='guest',welcomed=session?.welcomed;
    clearInterval(publishTimer);clearTimeout(searchTimer);
    for(const cleanup of cleanups)cleanup();
    cleanups=[];session=null;role=null;inviteLink='';
    nametags.clear();
    chat.add({system:true,text:reason});chat.setEnabled(false);
    panel.hidden=true;followHost.closest('label').hidden=true;
    port.setEditRelay(null);port.setRole('solo');
    port.setStatus(reason);
    setButton('Host session');
    if(wasGuest){
      clearInviteFromUrl();
      // A guest keeps the host's flyer as an ordinary local session.
      if(!welcomed)port.loadInitialFlyer();
    }
  }

  async function startHosting(){
    if(!port.hasFlyer())return;
    role='host';setButton('Starting…',{disabled:true});
    try{
      const transportName=chosenTransport();
      const transport=await createTransport(transportName,multiplayerConfig);
      const room=newRoomId(),host=new HostSession({transport,port,room});
      attach(host);
      listen(port.events,'flyer',()=>host.flyerChanged());
      listen(port.events,'mode',()=>host.modeChanged());
      await host.start();
      const url=new URL(inviteUrl(location.href,{room,host:transport.selfId}));
      if(transportName!==multiplayerConfig.transport)url.searchParams.set('transport',transportName);
      inviteLink=url.toString();
      port.setRole('host');chat.setEnabled(true);
      setButton('Stop hosting',{danger:true});
      showPanel('Hosting. Share the invite link; guests can edit while you are in Edit mode.');
      chat.add({system:true,text:'Session started. Press Enter to chat.'});
      copyInvite(true);
    }catch(error){
      console.error(error);
      if(session)await session.end(`Could not start hosting: ${error.message}`);
      else teardown(`Could not start hosting: ${error.message}`);
    }
  }

  async function joinFromInvite(){
    const name=await askName();
    if(name===null){clearInviteFromUrl();await port.loadInitialFlyer();return;}
    role='guest';port.setRole('guest');
    setButton('Leave session',{danger:true});
    followHost.checked=true;followHost.closest('label').hidden=false;
    showPanel('Connecting to the host…');
    port.setStatus('Connecting to the host…');
    try{
      const transport=await createTransport(chosenTransport(),multiplayerConfig);
      const guest=new GuestSession({transport,port,room:invite.room,hostId:invite.host,name});
      attach(guest);
      port.setEditRelay({
        place:(positions,cell)=>guest.requestEdit({op:'place',positions,cell}),
        remove:pos=>guest.requestEdit({op:'remove',pos}),
        cycle:pos=>guest.requestEdit({op:'cycle',pos}),
      });
      cleanups.push(
        guest.on('welcome',({name:assigned})=>{
          clearTimeout(searchTimer);chat.setEnabled(true);
          showPanel(`Connected as ${assigned}. You can edit while the host is in Edit mode.`);
          port.setStatus(`Joined as ${assigned}. Press Enter to chat.`);
        }),
        guest.on('playback',state=>{if(followHost.checked)port.followPlayback(state);}),
      );
      listen(port.events,'user-playback',()=>{followHost.checked=false;});
      listen(followHost,'change',()=>{if(followHost.checked&&guest.hostPlayback)port.followPlayback(guest.hostPlayback);});
      searchTimer=setTimeout(()=>{
        if(!guest.welcomed)showPanel('Still looking for the host… They may have stopped hosting, or your networks may not be able to connect directly.');
      },HOST_SEARCH_HINT_MS);
      await guest.start();
    }catch(error){
      console.error(error);
      if(session)await session.end(`Could not join: ${error.message}`);
      else teardown(`Could not join: ${error.message}`);
    }
  }

  async function copyInvite(quiet=false){
    try{await navigator.clipboard.writeText(inviteLink);$('mp-copy').textContent='Copied!';}
    catch{if(!quiet){$('mp-invite').select();$('mp-copy').textContent='Press Ctrl+C';}}
    setTimeout(()=>{$('mp-copy').textContent='Copy';},1800);
  }

  button.onclick=()=>{if(session)session.stop();else startHosting();};
  $('mp-copy').onclick=()=>copyInvite();
  $('mp-invite').onfocus=()=>$('mp-invite').select();
  // Say goodbye on close so others hear at once, not after a connection timeout.
  addEventListener('pagehide',()=>{session?.stop();});
  return {invite,joinFromInvite};
}
