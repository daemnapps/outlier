/* ═══════════════════════════════════════════════════════════════
   THE SHOP — a portal world.

   The worked example. A man clicks an ad and walks into the barbershop
   he already knows: the bell, the wait, the argument, the blue jar, the
   chair going up, the mirror, and the one thing he's been avoiding
   under his collar. Somewhere in the middle he learns what a razor
   bump actually is, by watching it happen, and what to do about it.
   He leaves with the product in his hand and the store already
   knowing four things about him without ever seeing a quiz.

   Every line here went through the brand's customer language filter.
   Every claim on the product card is a customer's own words, quoted.
   The pictures were generated from the prompts in prompts.md next to
   this file — regenerate them for your own shop.
   ═══════════════════════════════════════════════════════════════ */
window.PORTAL_WORLD = {
  id: 'barbershop',
  title: 'The Shop',
  voice: 'Barber',                          // who replies when nobody is named
  base: window.PORTAL_BASE || 'media/',     // where the pictures live, relative to the page
  theme: { accent: '#3aa0ff' },             // the blue in the jar

  brand: {
    name: 'DOUXDS',
    shopUrl: 'https://douxds.com',          // ← from your offer bank. The world appends what it learned.
    newTab: false,
    product: {
      name: 'CRUSH',
      what: 'Bump eliminator. The one that stays on the station next to the blue jar.',
      says: ['no stinging', 'light weight', 'bumps started disappearing'],   // customers' words, quoted
      // price: '$—',  price and offer come from your offer bank, never from here
    },
  },

  // what the world learns, and how to say it back at the door
  context: [
    { key: 'cut',   label: 'Your cut',   say: { fade: 'low fade + lineup', lineup: 'lineup', beard: 'beard shape-up', bald: 'bald, razor' } },
    { key: 'neck',  label: 'Your neck',  say: { some: 'a few bumps', marks: 'bumps + dark marks', ingrown: 'ingrown hairs', none: 'clear, keeping it that way' } },
    { key: 'last',  label: 'Last cut',   say: { '2w': 'two weeks', '1m': 'a month', long: 'a while' } },
    { key: 'shave', label: 'The neck',   say: { razor: 'razor', clippers: 'clippers, no guard', guard: 'trimmer + guard', none: 'untouched' } },
  ],

  // measure: { endpoint: 'https://…' },   // optional: every event also POSTs here

  beats: [
    {
      id: 'door', time: '10:40', eyebrow: 'Saturday · 10:40am', image: '00-door.jpg', sound: 'street', mood: '#4a2e22',
      lines: [
        { s: 'The bell hits the glass before you’re all the way in. Clippers. Aftershave. The game on the TV. You already know.' },
        { n: 'Tap the dots. Everything in here does something.' },
      ],
      hotspots: [
        { x: 0.44, y: 0.09, label: 'The bell', text: 'Same bell since you were somebody’s son. Everybody looks up. Nobody says anything.' },
      ],
      action: { type: 'tap', label: 'Walk in' },
    },
    {
      id: 'wait', time: '10:41', eyebrow: 'The wait', image: '01-wait.jpg', sound: 'shop', mood: '#3a2a22',
      lines: [
        { s: 'Six heads ahead of you. Nobody’s leaving. Nobody ever leaves.' },
        { who: 'Barber', t: 'Who got next?' },
        { y: 'Not you. Not for a while.' },
      ],
      hotspots: [
        { x: 0.82, y: 0.20, label: 'The clock', text: '10:41. It’s gonna say 2:15 before you’re in that chair. That’s the deal. You knew that when you came.' },
        { x: 0.22, y: 0.48, label: 'Unc', text: 'Been asleep since the first cut. Still ahead of you.' },
        { x: 0.78, y: 0.50, label: 'Little man', text: 'First fade'. He’s more nervous than you are.' },
      ],
      action: {
        type: 'choice', key: 'cut', who: 'Barber', ask: 'What you getting today?', next: 'Sit down',
        options: [
          { label: 'Low fade, lineup', value: 'fade', reply: 'Say less.' },
          { label: 'Just a lineup', value: 'lineup', reply: 'Alright. You keeping it tight.' },
          { label: 'Beard shape-up', value: 'beard', reply: 'I got you. That’s where it matters.' },
          { label: 'Bald, with the razor', value: 'bald', reply: 'Razor. Okay. We’re gonna talk about that.' },
        ],
      },
    },
    {
      id: 'talk', time: '12:10', eyebrow: 'Shop talk', image: '02-talk.jpg', sound: 'shop', mood: '#3a2a22',
      lines: [
        { s: 'An hour and a half in. The argument started before you sat down and nobody remembers how.' },
        { who: 'Barber', t: 'Bro, you can’t put him top five. Tell me I’m wrong.' },
      ],
      hotspots: [
        { x: 0.73, y: 0.54, label: 'The blue jar', text: 'Every comb in the shop lives in there. You never asked what the blue is. Nobody has.' },
        { x: 0.20, y: 0.12, label: 'The TV', text: 'Third quarter. Nobody’s actually watching. Everybody’s got an opinion.' },
      ],
      action: {
        type: 'choice', key: 'talk', who: 'Barber', ask: 'You in this or you staying out of it?', next: 'Keep waiting',
        options: [
          { label: 'I’m in. He’s top five.', value: 'in', reply: 'See, this man gets it.' },
          { label: 'Staying out of it.', value: 'out', reply: 'Smart. This goes another forty minutes.' },
          { label: 'Top three, actually.', value: 'bold', reply: 'Top THREE? Somebody get this man out my shop.' },
        ],
      },
    },
    {
      id: 'she-walks-in', time: '13:05', eyebrow: '1:05pm', image: '03-she-walks-in.jpg', sound: 'quiet', mood: '#5a3a2a',
      lines: [
        { s: 'The door opens and the whole room sits up. She’s got her son by the hand. Every man on this bench just fixed his collar at the same time.' },
        { y: 'You go to fix yours too. Your hand hits your neck first. You know what’s there. You been knowing.' },
      ],
      hotspots: [
        { x: 0.30, y: 0.42, label: 'Little man', text: 'Needs a cut. She’s already back on her phone. She’s got somewhere to be and it’s not here.' },
      ],
      action: {
        type: 'choice', key: 'neck', who: 'Barber', ask: 'Be honest with yourself. What’s under that collar?', next: 'Wait it out',
        options: [
          { label: 'A few bumps after I shave', value: 'some', reply: 'No shame in that. Almost every man on this bench got the same thing under his collar.' },
          { label: 'Bumps and dark marks, all down the neck', value: 'marks', reply: 'I’ve been there bro. It’s not just you. We’re getting to that in the chair.' },
          { label: 'Ingrown hairs I keep digging at', value: 'ingrown', reply: 'Stop digging. Real talk. Hold on till you’re in the chair.' },
          { label: 'Nothing yet. Trying to keep it that way', value: 'none', reply: 'Then stay with me. What he shows you in the chair is how you keep it that way.' },
        ],
      },
    },
    {
      id: 'chair', time: '14:15', eyebrow: '2:15pm', image: '04-chair.jpg', sound: 'clippers', mood: '#2e2320',
      lines: [
        { s: 'Your name. Finally. The chair’s still warm from the last guy. Click. Click. Click. He pumps it up till your head’s where he wants it.' },
        { y: 'The cape snaps open. Cold on your neck.' },
      ],
      hotspots: [
        { x: 0.48, y: 0.62, label: 'The pedal', text: 'Chrome. He hits it with his heel without looking. Three pumps. He knows your height.' },
        { x: 0.63, y: 0.34, label: 'The blue jar', text: 'Right where it always is.' },
      ],
      action: {
        type: 'choice', key: 'last', who: 'Barber', ask: 'When was the last time you were in here?', next: 'Head down',
        options: [
          { label: 'Two weeks', value: '2w', reply: 'Alright. Then you know the drill.' },
          { label: 'About a month', value: '1m', reply: 'Grew out on you. It’s all good. We’ll get it back.' },
          { label: 'Longer than I want to admit', value: 'long', reply: 'No worries. You’re here now. That’s the part that counts.' },
        ],
      },
    },
    {
      id: 'mirror', time: '14:22', eyebrow: '2:22pm', image: '05-mirror.jpg', sound: 'close', mood: '#3a2620',
      lines: [
        { s: 'Two fingers under your jaw. He tilts your head to the light. He’s not looking at the cut. He’s looking at your neck.' },
        { who: 'Barber', t: 'You been shaving this yourself?' },
      ],
      action: {
        type: 'choice', key: 'shave', who: 'Barber', ask: 'How you been doing your neck?', next: 'Look',
        options: [
          { label: 'Razor, every couple days', value: 'razor', reply: 'Yeah. That’s the bumps right there. Hold on. Let me show you something.' },
          { label: 'Clippers, no guard', value: 'clippers', reply: 'No guard. Okay. That’s basically a razor. Let me show you something.' },
          { label: 'Trimmer with a guard', value: 'guard', reply: 'That’s better than most. Still. Let me show you something.' },
          { label: 'I don’t touch the neck', value: 'none', reply: 'Then you’re ahead of the room. Let me show you something anyway.' },
        ],
      },
    },
    {
      id: 'lesson', time: '14:24', eyebrow: 'Here’s what nobody tells you', image: '05-mirror.jpg', sound: 'close', mood: '#3a2620',
      lines: [
        { who: 'Barber', t: 'Your hair grows curly. Shave it real close and the tip goes back under the skin instead of coming out. That’s the bump. Your skin’s fighting a hair that never left.' },
        { n: 'Drag the slider. Watch the hair.' },
      ],
      lesson: {
        kind: 'ingrown', who: 'Barber',
        sliderLabel: 'How close you shave',
        labels: ['coming out clean', 'cut at the skin', 'cut under the skin', 'curls back in', 'that’s the bump'],
        dig: {
          text: 'Now here’s where it flips. Most men dig at it.',
          label: 'Dig at it',
          result: 'now there’s a dark mark on top',
          reply: 'That’s the dark mark on top of the bump. Now your neck’s keeping a receipt for every one.',
        },
        ask: 'So what do I do?',
        steps: [
          'Hot towel first. Always. It softens everything up so the hair comes out instead of going under.',
          'Go with the grain. Never against it. Closer isn’t cleaner. Closer is the bump.',
          'Stop digging at it. Every time you dig you leave a mark that stays longer than the bump did.',
          'Keep something on the neck every night. That’s the part everybody skips, and it’s the part that works.',
        ],
      },
      action: { type: 'lesson', next: 'What do you keep on it?' },
    },
    {
      id: 'station', time: '14:31', eyebrow: '2:31pm', image: '06-station.jpg', sound: 'close', mood: '#2e2320', showProduct: true,
      lines: [
        { s: 'Hot towel. Steam in your eyes. He lays it on your neck and just leaves it there.' },
        { who: 'Barber', t: 'This right here. Stays on the station next to the blue jar. Neck, every night. No stinging, and it’s light, so you don’t feel like you got something on your face.' },
        { y: 'He puts it in your hand before you can ask what it is.' },
      ],
      hotspots: [
        { x: 0.38, y: 0.56, label: 'The towel', text: 'Hot enough to make you flinch. That’s the point. Two minutes under it and your skin’s ready.' },
      ],
      action: { type: 'tap', label: 'Alright' },
    },
    {
      id: 'aftershave', time: '14:40', eyebrow: '2:40pm', image: '07-aftershave.jpg', sound: 'close', mood: '#3a2620',
      lines: [
        { s: 'He cups his hands. You hear the bottle. You already know what’s coming.' },
      ],
      action: {
        type: 'hold', label: 'Hold for the sting', ms: 1300, haptic: [60, 40, 160], who: 'Barber',
        reply: 'Woo. Alright. Look at you. Two different people.', next: 'Look in the mirror',
      },
    },
    {
      id: 'exit', time: '14:48', eyebrow: '2:48pm · you’re out', image: '08-exit.jpg', sound: 'street', mood: '#5a3a22',
      lines: [
        { s: 'You catch yourself in the window on the way out. Then in the car door. Then in your phone.' },
        { who: 'Barber', t: 'Two weeks. Keep that on your neck at night. Come see me.' },
        { y: 'Four hours. Worth it. It’s always worth it.' },
      ],
      action: { type: 'exit', label: 'Take it with you', again: 'Back to the door' },
    },
  ],
};
