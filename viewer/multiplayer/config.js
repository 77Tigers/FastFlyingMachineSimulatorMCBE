// Multiplayer settings. To switch networking backends, register a new
// transport in transport.js and change `transport` here.
export const multiplayerConfig={
  // 'trystero': WebRTC, signalled through public Nostr relays (no server needed).
  // 'local': BroadcastChannel between tabs of this browser (offline testing).
  // Append ?transport=local to a URL to override this for one session.
  transport:'trystero',
  appId:'fastflyer-playground-v1',
  // Nostr relays used to find each other, in preference order. Each player
  // uses the first `relayCount` that answer, so host and guests normally pick
  // the same ones; they only need to share one. Relays come and go: these all
  // accepted Trystero's ephemeral events on 2026-10-11.
  nostrRelays:[
    'nos.lol','nostr-01.uid.ovh','basspistol.org','nostr.sathoarder.com','nostr.data.haus',
    'purplerelay.com','nostr.islandarea.net','nostr-relay.corb.net','bucket.coracle.social',
    'nostr-01.yakihonne.com','relay.mostro.network','relay.sigit.io','relay-can.zombi.cloudrodion.com',
    'schnorr.me','relay02.lnfi.network','yabu.me/v2','staging.yabu.me',
  ].map(host=>`wss://${host}`),
  relayCount:5,
  // Some strict NATs (mobile carriers, offices) need a TURN relay, e.g.
  // {urls:'turn:turn.example.com:3478',username:'user',credential:'secret'}.
  turnServers:[],
};
