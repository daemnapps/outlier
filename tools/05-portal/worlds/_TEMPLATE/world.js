/* ═══════════════════════════════════════════════════════════════
   YOUR WORLD — the template.

   Copy this folder, rename it after the place your customer already
   knows, and fill in every angle-bracket prompt. Stage 4 of the chain
   (the-chain/05--stage-4-assemble.md) writes this file for you from
   the world bible; this template is what it fills in, and what you
   edit afterwards.

   A world is played like a mission. The player stands in a wide plate
   and looks around it; a yellow marker says where to go; people talk
   in subtitles; the one thing to do is a wheel, a hold, a pickup, a
   scan or the exit. The HUD (cash, clock, stars, radar, objective) is
   drawn by the player and driven by the fields below.

   The rules, so the player does not have to guess:
   · every mission has ONE action: go, wheel, hold, get, scan or exit
   · lines are short: one thing somebody would actually say out loud
   · every wheel has a key. Keys become the fields your store receives
   · nothing here is invented: the lines come from the world bible,
     the reward card from the product file, quotes from real reviews
   · no em dashes in any string. They read as a tell.
   ═══════════════════════════════════════════════════════════════ */
window.PORTAL_WORLD = {
  id: '<slug-of-the-place>',                // e.g. 'barbershop'. Goes out with every event and on the exit link
  title: '<THE PLACE, AS THEY CALL IT>',    // e.g. 'THE SHOP'. The title card
  base: window.PORTAL_BASE || 'media/',     // where the pictures live, relative to the page. Leave it.
  theme: { accent: '#ffd23f' },             // objective yellow. Change only if the world has its own colour

  brand: {
    name: '<Brand name>',
    shopUrl: '<the page they land on, from your offer bank>',
    newTab: false,
    product: {
      name: '<Product name, exactly as on the label>',
      what: '<what it is and where it sits in this world, one line, in the customer language>',
      says: ['<a real review phrase>', '<another>', '<another>'],   // quoted on the reward card. Real words only.
      // price: '<from the offer bank>',
    },
  },

  player: { name: '<who they are in here>', cash: '<what is in their pocket, e.g. $40>' },

  // who talks, and the colour their name takes in the subtitles (cls: you barber ray tyrese mom nina, or add your own in the css)
  speakers: {
    you:    { name: 'You',    cls: 'you' },
    '<id>': { name: '<Name>', cls: 'barber' },
  },

  // what the world learns about the person, and how it is said back on the passed screen.
  // Each key here should be a question your quiz funnel would have asked.
  context: [
    { key: '<key>', label: '<Label>', say: { '<value>': '<how it reads>' } },
  ],

  // things they can pick up. They show in the slots bottom-right
  items: [ { id: '<item>', name: '<Product name>', short: '<5 letters>' } ],

  // measure: { endpoint: '<https://… receives every event as JSON>' },

  // the wide plates you look around in (16:9), and what the room sounds like (street / shop / chair / quiet)
  scenes: {
    '<scene>': { plate: '<p-scene.jpg, from prompts.md>', ratio: 16 / 9, mood: '<#hex fallback if the picture is missing>', sound: 'shop' },
  },

  // the radar: rooms as blocks (0..1 of the map) and spots as where you stand in each mission
  map: {
    rooms: [ { x: .04, y: .06, w: .92, h: .58 }, { x: .04, y: .74, w: .92, h: .22, fill: '#22303a', label: 'street' } ],
    spots: { '<scene>': { x: .5, y: .5 } },
  },

  missions: [
    // ── 0 · outside: where they arrive from the ad ───────────────────
    {
      id: '<pull-up>', scene: '<scene>', heading: .5, facing: 0, clock: '<H:MM on the world clock>',
      title: '<THE PLACE>', sub: '<Saturday · 10:40am>', tag: '<one line under the title>',   // the title card, first mission only
      objective: 'Go to ~y~<the place>~s~',         // ~y~ yellow ~g~ green ~b~ blue, ~s~ back to white
      marker: { id: '<door>', x: .5, y: .58, label: '<The place>', look: '<l-bell.jpg, optional close-up shown when tapped>' },
      hotspots: [                                    // side things. kind: look (white) or talk (blue)
        { id: '<thing>', x: .33, y: .40, label: '<The thing>', text: '<what it means to someone who knows this place>' },
        { id: '<person>', x: .2, y: .5, label: '<Name>', kind: 'talk', look: '<l-name.jpg>', lines: [ { who: '<id>', t: '<a line>' } ] },
      ],
      lines: [                                       // subtitles after the marker is tapped. who: think = a thought
        { who: 'think', t: '<what they notice, one breath>', sfx: 'bell' },
      ],
      action: { type: 'go', label: '<Walk in>' },
    },

    // ── a wheel: the question the funnel would have asked ───────────
    {
      id: '<the-wait>', scene: '<scene>', heading: .35, facing: -40, clock: '<H:MM>', special: .15,
      note: { title: '<Wait time>', text: '<a notification, top left>' },
      objective: 'Find ~y~a seat~s~',
      marker: { id: '<seat>', x: .62, y: .70, label: '<A seat>' },
      lines: [ { who: '<id>', t: '<what they say when you sit down>' } ],
      action: {
        type: 'wheel', key: '<key>', q: '<the question, as the person asks it>', hint: '<who is asking>', who: '<id>',
        options: [
          { t: '<answer>', v: '<value>', say: '<what the asker says back>' },
          { t: '<answer>', v: '<value>', say: '<reply>' },
        ],
      },
    },

    // ── a hold: something that happens to them ──────────────────────
    {
      id: '<the-chair>', heading: .5, facing: 90, clock: '<H:MM>',      // no scene: stays in the room, turns to look
      objective: 'Get in ~y~the chair~s~',
      marker: { id: '<chair>', x: .5, y: .62, label: '<The chair>', look: '<l-pump.jpg>' },
      lines: [ { who: '<id>', t: '<a line>', sfx: 'clippers' } ],
      action: { type: 'hold', id: '<cut>', label: '<Hold still>', sfx: true, after: '<what happened while they held>' },
    },

    // ── the scan: the lesson, drawn, with a slider ──────────────────
    {
      id: '<the-scan>', heading: .5, facing: 90, clock: '<H:MM>',
      objective: 'Look ~y~closer~s~',
      marker: { id: '<bump>', x: .5, y: .48, label: '<Look closer>', look: '<l-neck.jpg>' },
      lines: [ { who: '<id>', t: '<Watch what the blade does.>' } ],
      action: { type: 'scan', lesson: {
        title: '<One hair, up close>', low: '<leave some>', high: '<skin close>', start: 15,
        s0: '<slider at the start>', s1: '<a little closer>', s2: '<under the skin>', s3: '<that is the bump>',
        dig: '<Dig at it>', sDig: '<what digging does>', fix: '<Put PRODUCT on it>', sFix: '<what the product does, in their words>',
        sNo: '<nothing to touch yet>', done: '<Got it>',
      } },
    },

    // ── the hand-over: the product, from a person, where it would really be ──
    {
      id: '<the-handoff>', heading: .55, facing: 0, clock: '<H:MM>', special: 1,
      objective: 'Talk to ~y~<Name>~s~',
      marker: { id: '<name>', x: .55, y: .5, label: '<Name>', kind: 'talk', look: '<l-product.jpg>' },
      lines: [ { who: '<id>', t: '<what they say handing it over. What it is, where it sits, what to do with it. Never what it delivers.>' } ],
      action: { type: 'get', item: '<item>', label: '<Keep it>' },
    },

    // ── mission passed: the door ────────────────────────────────────
    {
      id: 'mission-passed', scene: '<scene>', heading: .5, facing: 90, clock: '<H:MM>', cash: '$0',
      objective: 'Look ~y~fresh~s~',
      marker: { id: '<fresh>', x: .5, y: .45, label: '<The mirror>', look: '<l-fresh.jpg>' },
      lines: [ { who: '<id>', t: '<the last line>', cash: '$0', sfx: 'bell' } ],
      action: {
        type: 'exit', title: 'MISSION PASSED', sub: '<The place · Saturday>', rewardLabel: 'reward unlocked', cta: '<Cop PRODUCT>',
        stats: [ ['<Paid>', '<$40>'], ['<Tip>', '<you know better>'] ],   // the player adds time, things clocked, the scan, and every context key
      },
    },
  ],
};
