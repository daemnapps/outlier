/* ═══════════════════════════════════════════════════════════════
   YOUR WORLD — the template.

   Copy this folder, rename it after the place your customer already
   knows, and fill in every angle-bracket prompt. Stage 4 of the chain
   (the-chain/05--stage-4-assemble.md) writes this file for you from
   the world bible; this template is what it fills in, and what you
   edit afterwards.

   The rules, so the player does not have to guess:
   · every beat has ONE action: tap, choice, hold, lesson or exit
   · lines are short. A sense line (s) is one breath. A spoken line (t)
     is one thing somebody would actually say out loud
   · every choice has a key. Keys become the fields your store receives
   · nothing here is invented: the lines come from the world bible,
     the product card from the product file, quotes from real reviews
   ═══════════════════════════════════════════════════════════════ */
window.PORTAL_WORLD = {
  id: '<slug-of-the-place>',                // e.g. 'barbershop' — goes out with every event and on the exit link
  title: '<The place, as they call it>',    // e.g. 'The Shop' — top left of every beat
  voice: '<who replies when nobody is named>', // e.g. 'Barber'
  base: window.PORTAL_BASE || 'media/',     // where the pictures live, relative to the page. Leave it.
  theme: { accent: '<#hex — one colour that lives in the world>' },

  brand: {
    name: '<Brand name>',
    shopUrl: '<the page they land on — from your offer bank>',
    newTab: false,
    product: {
      name: '<Product name, exactly as on the label>',
      what: '<what it is, in the words of the product file, one line>',
      says: ['<a real review phrase>', '<another>', '<another>'],   // quoted on the card. Real words only.
      // price: '<from the offer bank>', priceNote: '<from the offer bank>',
      // image: '<file in media/ — a photo of the real product, never a generated one>',
    },
  },

  // what the world learns about the person, and how it is said back to them at the door.
  // Each key here should be a question your quiz funnel would have asked.
  context: [
    { key: '<key>', label: '<Label>', say: { '<value>': '<how it reads on the chip>' } },
  ],

  // measure: { endpoint: '<https://… receives every event as JSON>' },

  beats: [
    // ── 1 · the threshold: where they arrive from the ad ────────────
    {
      id: 'door', time: '<HH:MM 24h — the clock in the world>', eyebrow: '<a few words above the text>',
      image: '<00-door.jpg — generated from prompts.md>', sound: 'street', mood: '<#hex fallback if the picture is missing>',
      lines: [
        { s: '<what they see, hear, smell in one breath>' },
        { n: '<a quiet note in small type, optional>' },
      ],
      hotspots: [
        { x: 0.5, y: 0.1, label: '<the thing>', text: '<what it means to someone who knows this place>' },
      ],
      action: { type: 'tap', label: '<the first thing they do — Walk in, Sit down…>' },
    },

    // ── 2 · a beat with a choice: the quiz question, in disguise ────
    {
      id: '<beat-id>', time: '<HH:MM>', eyebrow: '<…>', image: '<01-….jpg>', sound: 'shop',
      lines: [
        { s: '<sense>' },
        { who: '<Name>', t: '<a spoken line>' },
        { y: '<a thought in their own head, italic>' },
      ],
      action: {
        type: 'choice', key: '<context key>', who: '<who asks>', ask: '<the question, as this person would ask it>', next: '<label of the button after they answer>',
        options: [
          { label: '<answer 1>', value: '<v1>', reply: '<what the asker says back — reassurance, never a sell>' },
          { label: '<answer 2>', value: '<v2>', reply: '<…>' },
        ],
      },
    },

    // ── 3 · the lesson: shown, not told ─────────────────────────────
    {
      id: 'lesson', time: '<HH:MM>', eyebrow: '<…>', image: '<reuse the mirror / close frame>', sound: 'close',
      lines: [
        { who: '<Name>', t: '<the one-sentence version of what is really going on, in their words>' },
        { n: 'Drag the slider.' },
      ],
      lesson: {
        kind: 'ingrown',                 // the built-in cutaway. Other kinds: add them to LESSONS in portal.js
        who: '<Name>',
        sliderLabel: '<what the slider does>',
        labels: ['<stage 0>', '<stage 1>', '<stage 2>', '<stage 3>', '<stage 4>'],
        dig: { text: '<the mistake people make>', label: '<the button>', result: '<the label after>', reply: '<what it costs them>' },
        ask: '<So what do I do?>',
        steps: ['<do this>', '<and this>', '<and this>', '<and keep something on it — this is where the product enters, without a name>'],
      },
      action: { type: 'lesson', next: '<label>' },
    },

    // ── 4 · the product, where it lives in the world ─────────────────
    {
      id: 'station', time: '<HH:MM>', eyebrow: '<…>', image: '<….jpg>', sound: 'close', showProduct: true,
      lines: [
        { s: '<sense>' },
        { who: '<Name>', t: '<how they hand it over — from the product file, in customer words, no claims the file does not back>' },
      ],
      action: { type: 'tap', label: '<…>' },
    },

    // ── 5 · a beat you feel: hold ────────────────────────────────────
    {
      id: '<…>', time: '<HH:MM>', eyebrow: '<…>', image: '<….jpg>', sound: 'close',
      lines: [{ s: '<sense>' }],
      action: { type: 'hold', label: '<Hold for the …>', ms: 1300, haptic: [60, 40, 160], who: '<Name>', reply: '<…>', next: '<…>' },
    },

    // ── 6 · the door out ─────────────────────────────────────────────
    {
      id: 'exit', time: '<HH:MM>', eyebrow: '<…>', image: '<….jpg>', sound: 'street',
      lines: [
        { s: '<sense>' },
        { who: '<Name>', t: '<the last thing they say to you>' },
      ],
      action: { type: 'exit', label: '<Take it with you>', again: '<Back to the door>' },
    },
  ],
};
