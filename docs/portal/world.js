/* ═══════════════════════════════════════════════════════════════
   THE SHOP, a portal world built like a mission.

   You click an ad and you are standing outside the barbershop you
   already know, on a Saturday, with forty dollars in your pocket.
   The yellow marker says go in. Ray is holding court. The wait is
   four hours. She walks in with her son and the whole room sits up.
   You get in the chair, you check the mirror, and there they are on
   your neck, same as last time. Somewhere in the middle you watch
   what the blade actually does to a hair, and the barber hands you
   the one thing he keeps on the station for it. MISSION PASSED.

   Every line went through the brand's customer language filter.
   Every quote on the reward card is a customer's own words.
   Every picture was generated from prompts.md next to this file,
   in the GTA loading-screen style, from the brand's own shop set,
   cast and product references. Regenerate them for your own shop.
   ═══════════════════════════════════════════════════════════════ */
window.PORTAL_WORLD = {
  id: 'barbershop',
  title: 'THE SHOP',
  base: window.PORTAL_BASE || 'media/',      // where the pictures live, relative to the page
  theme: { accent: '#ffd23f' },              // objective yellow

  brand: {
    name: 'DOUXDS',
    shopUrl: 'https://douxds.com',           // ← from your offer bank. The world appends what it learned.
    newTab: false,
    product: {
      name: 'CRUSH',
      what: 'The bump serum the barber keeps on the station next to the blue jar. On the neck tonight, gone before the next cut.',
      says: ['no stinging', 'light weight', 'bumps started disappearing'],   // customers' words, quoted
      // price: '$--',  price and offer come from your offer bank, never from here
    },
  },

  player: { name: 'Marcus', cash: '$40' },

  // who talks, and the colour their name takes in the subtitles
  speakers: {
    you:    { name: 'You',    cls: 'you' },
    barber: { name: 'Omar',   cls: 'barber' },
    ray:    { name: 'Ray',    cls: 'ray' },
    tyrese: { name: 'Tyrese', cls: 'tyrese' },
    mom:    { name: 'Her',    cls: 'mom' },
    nina:   { name: 'Nina',   cls: 'nina' },
  },

  // what the world learns, and how to say it back at the door
  context: [
    { key: 'cut',   label: 'Your cut',   say: { fade: 'low fade + lineup', lineup: 'lineup', beard: 'beard shape-up', bald: 'bald, razor' } },
    { key: 'last',  label: 'Last cut',   say: { '2w': 'two weeks', '1m': 'a month', long: 'a while' } },
    { key: 'neck',  label: 'Your neck',  say: { some: 'a few bumps', marks: 'bumps + dark marks', ingrown: 'ingrown hairs', none: 'clear, keeping it that way' } },
    { key: 'shave', label: 'The neck',   say: { razor: 'razor', clippers: 'clippers, no guard', guard: 'trimmer + guard', none: 'untouched' } },
  ],

  // things you can pick up; they show in the slots bottom-right
  items: [ { id: 'crush', name: 'CRUSH', short: 'CRUSH' } ],

  // measure: { endpoint: 'https://…' },   // optional: every event also POSTs here

  // the wide plates you look around in (16:9), and what the room sounds like
  scenes: {
    street:  { plate: 'p-street.jpg',  ratio: 16 / 9, mood: '#3f2a20', sound: 'street' },
    wait:    { plate: 'p-wait.jpg',    ratio: 16 / 9, mood: '#4a3124', sound: 'shop' },
    door:    { plate: 'p-door.jpg',    ratio: 16 / 9, mood: '#3a2c26', sound: 'shop' },
    chair:   { plate: 'p-chair.jpg',   ratio: 16 / 9, mood: '#2c2320', sound: 'chair' },
    counter: { plate: 'p-counter.jpg', ratio: 16 / 9, mood: '#2f2622', sound: 'shop' },
  },

  // the radar: rooms as blocks, spots as where you stand (0..1 of the map)
  map: {
    rooms: [
      { x: .04, y: .06, w: .92, h: .58 },
      { x: .04, y: .06, w: .92, h: .16, fill: '#354656', label: 'counter' },
      { x: .06, y: .30, w: .34, h: .30, fill: '#2f3d4a', label: 'wait' },
      { x: .52, y: .30, w: .40, h: .30, fill: '#2f3d4a', label: 'chairs' },
      { x: .04, y: .74, w: .92, h: .22, fill: '#22303a', label: 'street' },
    ],
    spots: { street: { x: .5, y: .86 }, door: { x: .5, y: .66 }, wait: { x: .22, y: .45 }, chair: { x: .72, y: .45 }, counter: { x: .5, y: .16 } },
  },

  missions: [
    /* 0 · outside */
    {
      id: 'pull-up', scene: 'street', heading: .5, facing: 0, clock: '10:40',
      title: 'THE SHOP', sub: 'Saturday · 10:40am', tag: 'Forty dollars. A four hour wait. Same as it ever was.',
      objective: 'Go to ~y~the Shop~s~',
      marker: { id: 'door', x: .50, y: .58, label: 'The Shop', look: 'l-bell.jpg' },
      hotspots: [
        { id: 'pole', x: .33, y: .40, label: 'The pole', text: 'Still spinning. Been spinning since you were somebody’s son.' },
        { id: 'sign', x: .66, y: .34, label: 'The sign', text: 'WALK-INS WELCOME. Everybody in there is a walk-in. That is the problem.' },
      ],
      lines: [
        { who: 'think', t: 'The bell hits the glass before you’re all the way in. Clippers. Aftershave. The game on the TV.', sfx: 'bell' },
        { who: 'think', t: 'You already know.' },
      ],
      action: { type: 'go', label: 'Walk in' },
    },

    /* 1 · the wait */
    {
      id: 'the-wait', scene: 'wait', heading: .35, facing: -40, clock: '10:41',
      objective: 'Find ~y~a seat~s~ and wait', special: .15,
      note: { title: 'Wait time', text: 'About four hours. Three ahead of you, and one of them is Ray.' },
      marker: { id: 'seat', x: .62, y: .70, label: 'A seat' },
      hotspots: [
        { id: 'tv', x: .86, y: .22, label: 'The TV', text: 'Third quarter. Nobody in here has watched a first quarter in years.' },
        { id: 'tyrese', x: .20, y: .52, label: 'Tyrese', kind: 'talk', look: 'l-tyrese.jpg', lines: [ { who: 'tyrese', t: 'Bro look at this. Chalk lineup. Fifty dollars.' }, { who: 'think', t: 'It does look like chalk.' } ] },
        { id: 'jar', x: .48, y: .44, label: 'The blue jar', look: 'l-jar.jpg', text: 'Same blue. Same combs. Same water since the last time you sat here.' },
      ],
      lines: [
        { who: 'ray', t: 'You good gang? He got three ahead of you. Sit down.' },
        { who: 'think', t: 'The chair is warm. Somebody just got up out of it and they still aren’t done.' },
      ],
      action: {
        type: 'wheel', key: 'cut', q: 'What we getting?', hint: 'Ray asks. Everybody asks.', who: 'ray',
        options: [
          { t: 'Low fade + lineup', v: 'fade',   say: 'Fade and a line. Sit tight, he does that with his eyes closed.' },
          { t: 'Just a lineup',     v: 'lineup', say: 'Lineup. Twenty minutes, four hours from now.' },
          { t: 'Beard shape-up',    v: 'beard',  say: 'Shape-up. Tell him easy on the neck, that razor bites.' },
          { t: 'Bald, razor',       v: 'bald',   say: 'Bald? Respect. Bring a towel, that razor is no joke.' },
        ],
      },
    },

    /* 2 · barbershop talk */
    {
      id: 'the-talk', heading: .2, facing: -60, clock: '11:52',
      objective: 'Survive ~y~the talk~s~', special: .4,
      marker: { id: 'ray', x: .18, y: .48, label: 'Ray', kind: 'talk', look: 'l-ray.jpg' },
      lines: [
        { who: 'ray', t: 'Fifteen dollars. Walk in, sit down, cut. That was the whole thing.' },
        { who: 'tyrese', t: 'Fifteen dollars and he took your hairline with him.' },
        { who: 'ray', t: 'Against the grain on a child. That was the law back then, ask anybody.' },
        { who: 'think', t: 'Your neck itches just hearing it.' },
        { who: 'ray', t: 'Head used to be tingling all the way home. That is how you knew it was a real cut.' },
      ],
      action: {
        type: 'wheel', key: 'last', q: 'Last time you was in here?', hint: 'Ray, squinting at your line.', who: 'ray',
        options: [
          { t: 'Two weeks', v: '2w',   say: 'Two weeks? Then why your neck look like that, king.' },
          { t: 'A month',   v: '1m',   say: 'A month. That is why he got three ahead of you.' },
          { t: 'A while',   v: 'long', say: 'A while. Yeah. We can tell.' },
        ],
      },
    },

    /* 3 · she walks in */
    {
      id: 'she-walks-in', scene: 'door', heading: .5, facing: 180, clock: '12:30',
      objective: 'Don’t ~y~stare~s~',
      marker: { id: 'her', x: .50, y: .55, label: 'The door', look: 'l-mom.jpg' },
      lines: [
        { who: 'think', t: 'Every back in the room straightens. Ray takes his hat off.' },
        { who: 'mom', t: 'Just a shape-up for him. How long is the wait?' },
        { who: 'ray', t: 'For you? Twenty minutes.' },
        { who: 'think', t: 'It is not twenty minutes.', stars: 1, note: { title: 'Wanted', text: 'You looked a second too long. Everybody saw.' } },
        { who: 'tyrese', t: 'Bro. The TV. Look at the TV.' },
      ],
      action: { type: 'go', label: 'Look at the TV', ghost: true },
    },

    /* 4 · the chair */
    {
      id: 'the-chair', scene: 'chair', heading: .5, facing: 90, clock: '2:36', stars: 0, special: .7,
      objective: 'Get in ~y~the chair~s~',
      marker: { id: 'chair', x: .50, y: .62, label: 'The chair', look: 'l-pump.jpg' },
      hotspots: [
        { id: 'station', x: .82, y: .40, label: 'The station', text: 'Spray bottle. Neck brush. Pomade. And a black tube with a gold cap you don’t remember from last time.' },
      ],
      lines: [
        { who: 'barber', t: 'Come on king. What we doing?', sfx: 'clippers' },
        { who: 'think', t: 'Foot on the pump. Up. Up. Up. Cape snaps. The same three seconds since forever.' },
        { who: 'barber', t: 'Say less. Hold still.' },
      ],
      action: { type: 'hold', id: 'cut', label: 'Hold still', sfx: true, after: 'With the grain on the top. Then he turns the clippers around on your neck. You know what is coming.' },
    },

    /* 5 · the mirror */
    {
      id: 'the-mirror', heading: .5, facing: 90, clock: '2:58',
      objective: 'Check ~y~the mirror~s~',
      marker: { id: 'neck', x: .50, y: .48, label: 'Your neck', look: 'l-neck.jpg' },
      lines: [
        { who: 'think', t: 'There they are. Same spot as last time. You have been pulling your collar up over them for two years.' },
        { who: 'barber', t: 'That is the razor, brother. Not you. Every man in this room has them somewhere.' },
      ],
      action: {
        type: 'wheel', key: 'neck', q: 'What you seeing?', hint: 'Omar, tilting your chin.', who: 'barber',
        options: [
          { t: 'A few bumps',       v: 'some',    say: 'A few. Caught it early. That is the easy one.' },
          { t: 'Bumps + dark marks', v: 'marks',   say: 'Bumps and marks. You been digging at them. I can tell.' },
          { t: 'Ingrown hairs',     v: 'ingrown', say: 'Ingrowns. The hair curls back in on you. Watch, I will show you.' },
          { t: 'Nothing, keeping it that way', v: 'none', say: 'Clean neck. Rare. Keep it that way, king.' },
        ],
      },
    },

    /* 6 · the scan */
    {
      id: 'the-scan', heading: .5, facing: 90, clock: '3:02',
      objective: 'Look ~y~closer~s~',
      marker: { id: 'bump', x: .50, y: .48, label: 'Look closer', look: 'l-neck.jpg' },
      lines: [ { who: 'barber', t: 'Watch what the blade does. Slide it.' } ],
      action: {
        type: 'scan',
        lesson: {
          title: 'One hair, up close', low: 'leave some', high: 'skin close', start: 15,
          s0: 'Left a little. The hair stays out where it belongs.',
          s1: 'Closer. The tip gets sharp and starts to bend.',
          s2: 'Under the skin now. The curl comes back on itself and pushes in.',
          s3: 'That is the bump. Not dirt, not a pimple. A hair growing back into you.',
          dig: 'Dig at it', sDig: 'And now it is a dark mark that stays months after the bump is gone. That is the one you see every morning.',
          fix: 'Put CRUSH on it', sFix: 'Soft enough that the hair lets go and comes back out. Night after night the bump goes down and the mark fades with it.',
          sNo: 'Nothing to touch yet. Shave closer and watch.', done: 'Got it',
        },
      },
    },

    /* 7 · the blue jar */
    {
      id: 'the-jar', scene: 'counter', heading: .5, facing: 0, clock: '3:10',
      objective: 'Find ~y~the blue jar~s~',
      marker: { id: 'jar', x: .42, y: .62, label: 'The blue jar', look: 'l-jar.jpg' },
      hotspots: [
        { id: 'shelf', x: .70, y: .30, label: 'The shelf', text: 'White and blue bottles. Black and gold ones. Paper price tags. He sells what he uses.' },
        { id: 'till', x: .12, y: .58, label: 'The till', text: 'Cash only. Same sign. Same tape holding the sign.' },
      ],
      lines: [
        { who: 'barber', t: 'Combs go in the blue. Then the razor goes on you.' },
        { who: 'barber', t: 'Which one you been using on your own neck at home?' },
      ],
      action: {
        type: 'wheel', key: 'shave', q: 'At home you use…', hint: 'Omar, not judging. Judging a little.', who: 'barber',
        options: [
          { t: 'A razor',            v: 'razor',    say: 'Razor. Yeah. That is the whole story right there.' },
          { t: 'Clippers, no guard', v: 'clippers', say: 'No guard on the neck? King.' },
          { t: 'Trimmer + guard',    v: 'guard',    say: 'Guard on. Smart. Bumps still find a way, though.' },
          { t: 'I don’t touch it',   v: 'none',     say: 'Leave it to me. Good.' },
        ],
      },
    },

    /* 8 · the handoff */
    {
      id: 'the-handoff', heading: .55, facing: 0, clock: '3:14', special: 1,
      objective: 'Talk to ~y~Omar~s~',
      marker: { id: 'omar', x: .55, y: .50, label: 'Omar', kind: 'talk', look: 'l-crush.jpg' },
      lines: [
        { who: 'barber', t: 'This is what I keep on the station for the ones that bump up.' },
        { who: 'barber', t: 'No sting. Light. On the neck tonight, and the next time you sit here we are not having this talk.' },
        { who: 'think', t: 'Black tube. Gold cap. He does not sell anything he does not use.' },
      ],
      action: { type: 'get', item: 'crush', label: 'Keep it' },
    },

    /* 9 · aftershave */
    {
      id: 'aftershave', heading: .45, facing: 0, clock: '3:16',
      objective: 'Take ~y~the sting~s~',
      marker: { id: 'sting', x: .48, y: .52, label: 'Aftershave', look: 'l-aftershave.jpg' },
      lines: [
        { who: 'think', t: 'Slap. Cold. Eyes water. Same as always.', sfx: 'spray' },
        { who: 'barber', t: 'Put the CRUSH on tonight and you will not feel that next time.' },
        { who: 'nina', t: 'Text from DOUXDS: Omar told us you came through. Your neck is on the list, king.', note: { title: 'New message', text: 'Nina · DOUXDS' } },
      ],
      action: { type: 'hold', id: 'sting', label: 'Take it', after: 'Fresh. Tingling all the way home.' },
    },

    /* 10 · mission passed */
    {
      id: 'mission-passed', scene: 'chair', heading: .5, facing: 90, clock: '3:18', cash: '$0',
      objective: 'Look ~y~fresh~s~',
      marker: { id: 'fresh', x: .50, y: .45, label: 'The mirror', look: 'l-fresh.jpg' },
      lines: [
        { who: 'ray', t: 'Now that is a cut.' },
        { who: 'think', t: 'Forty dollars. Four hours. Worth it. Same as it ever was.', cash: '$0', sfx: 'bell' },
      ],
      action: {
        type: 'exit', title: 'MISSION PASSED', sub: 'The Shop · Saturday', rewardLabel: 'reward unlocked', cta: 'Cop CRUSH',
        stats: [ ['Paid', '$40'], ['Tip', 'you know better'], ['The talk', 'survived'] ],
      },
    },
  ],
};
